import app
from app import current_hour, daytime_temperature_target, nighttime_temperature_target, \
    daytime_span, batch_size, url, hours
from app.parsing import get_temperatures_forecast
from app.model_RL import eval_strat, p_model_RL, q_model_RL
from renew_model import DDPG

from tabulate import tabulate
import pandas as pd
import numpy as np
import time
from datetime import datetime

import logging

logging.basicConfig(level=logging.INFO, filename='heatRL.log', format='%(asctime)s %(levelname)s:%(message)s',
                    filemode='a')
logger = logging.getLogger(__name__)

import torch
import torch.optim as optim

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def renew_model_job(experience_df):
    p_model_RL.load_state_dict(
        torch.load('./app/model/p_modelRL_3hours_double_tout_v4.pt', map_location=torch.device(DEVICE)))
    q_model_RL.load_state_dict(
        torch.load('./app/model/v_modelRL_3hours_double_tout_v4.pt', map_location=torch.device(DEVICE)))
    model_train_dict = dict(policy_model=p_model_RL,
                            policy_max_grad_norm=float('inf'),
                            policy_optimizer_fn=lambda net, lr: optim.Adam(net.parameters(), lr=lr),
                            policy_optimizer_lr=0.0005,
                            policy_optim_scheduler=lambda optimizer: optim.lr_scheduler.ExponentialLR(optimizer,
                                                                                                      gamma=0.998),
                            value_model=q_model_RL,
                            value_max_grad_norm=float('inf'),
                            value_optimizer_fn=lambda net, lr: optim.Adam(net.parameters(), lr=lr),
                            value_optimizer_lr=0.0005,
                            value_optim_scheduler=lambda optimizer: optim.lr_scheduler.ExponentialLR(optimizer,
                                                                                                     gamma=0.995),
                            update_target_every_steps=5,
                            tau=0.001,
                            df=experience_df)

    train_dict = dict(seed=12, gamma=0.7, max_episodes=11)
    agent = DDPG(**model_train_dict)
    agent.train(**train_dict)
    p_l = round(sum(agent.p_loss), 1)
    v_l = round(sum(agent.v_loss), 1)

    torch.save(p_model_RL.state_dict(), './app/model/p_modelRL_3hours_double_tout_v4.pth')
    torch.save(q_model_RL.state_dict(), './app/model/v_modelRL_3hours_double_tout_v4.pth')
    print('Successfuly renewed, mean_5 p_loss: {}, mean_5 v_loss: {}'.format(p_l, v_l))
    return 'p_loss: {}, v_loss: {}'.format(p_l, v_l)


def next_temp(state, Theat):
    betta = 1 + (state[4] + state[5] + state[3] / 5) / 3
    toutside = (state[1] + state[2]) / 2
    tinside = state[0]
    Q = (Theat - 42.2) / 12
    t = toutside + Q / 0.07 + (tinside - toutside - Q / 0.07) / (np.exp(3 * betta / 70))
    return t


def job(url):
    experience_df = pd.read_csv('./data/experience_RL.csv')
    input_df = pd.read_csv('./data/input_data_RL.csv')
    output_df = pd.read_csv('./data/output_data_RL.csv')
    # weights = [1 + int(100 * i / len(experience_df)) for i in range(len(experience_df))]
    p_model_RL.load_state_dict(
        torch.load('./app/model/p_modelRL_3hours_double_tout_v4.pt', map_location=torch.device(DEVICE)))
    p_model_RL.eval()

    if daytime_span[0] <= current_hour <= daytime_span[1]:
        ttarget_current = daytime_temperature_target
    else:
        ttarget_current = nighttime_temperature_target

    if daytime_span[0] <= current_hour + 3 <= daytime_span[1]:
        ttarget_next = daytime_temperature_target
    else:
        ttarget_next = nighttime_temperature_target

    temperature_current, temperature_next, wind, humidity, cloudiness = get_temperatures_forecast(url)
    Tin_current = input_df['Tinside'].values[0]

    state_current = [Tin_current, temperature_current, temperature_next, wind, humidity, cloudiness,
                     ttarget_current, ttarget_next]
    reward = -abs(Tin_current - ttarget_current)
    action = round(eval_strat.select_action(p_model_RL, state_current), 1)
    state_next = [0.0 for i in range(len(state_current) + 1)]
    state_next[1] = next_temp(state_current, action)
    input_df.loc[0, 'Tinside'] = round(state_next[1], 1)
    input_df.to_csv('./data/input_data_RL.csv', index=False)
    date = datetime.strftime(datetime.now(), '%d.%m.%y %H:00')

    output_df.loc[0, 'Theat'] = action
    output_df.to_csv('./data/output_data_RL.csv', index=False)

    if datetime.now().hour in hours:
        experience_df.loc[
            len(experience_df.index) - 1, ['Reward', 'Tinside_n', 'Toutside_n', 'Toutside_n2', 'W_n', 'Hd_n',
                                           'Cl_n', 'Ttarget_current_n', 'Ttarget_next_n']] = \
            [reward] + state_current
        experience_df.loc[len(experience_df.index)] = [date] + state_current + [action] + state_next
        # experience_df.loc[:, 'weights'] = weights
        experience_df.to_csv('./data/experience_RL.csv', index=False)

    data = [state_current + [round(action, 1)]]
    headers = ['Tвн', 'Tнар', 'Тнар_сл', 'W', 'Hd', 'Cl', 'Target', 'Target_next', 'Tпод']
    print(tabulate(data, headers=headers))

    logs_dict = dict(Tвн=state_current[0], Tнар=state_current[1], Тнар_сл=state_current[2], W=state_current[3],
                     Hd=state_current[4], Cl=state_current[5], Target=state_current[6], Target_next=state_current[7],
                     Tпод=round(action, 1))
    return logs_dict


if __name__ == '__main__':
    while datetime.now() < datetime(2024, 3, 17, 23, 0):
        try:
            logs_dict = job(url)
            experience_df = pd.read_csv('./data/experience_RL.csv')
            experience_df = experience_df[1:-1]
            if len(experience_df[1:-1]) > batch_size:
                renew_result_losses = renew_model_job(experience_df)
                logger.info('%s results of RL model updating', renew_result_losses)
            logger.info('%s results of modeling', logs_dict)
            time.sleep(3600)
        except Exception as e:
            logger.error("Error logged:", exc_info=True)
            pass
