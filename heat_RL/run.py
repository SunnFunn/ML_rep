# импорт из проектной папки app всех необходимых для работы модели переменных, функций, классов и моделей
from app import daytime_temperature_target, nighttime_temperature_target, \
    daytime_span, batch_size, url_msk, modeling_period, forecast_hours
from app.parsing import get_temperatures_forecast
from app.model_RL import eval_strat, p_model_RL, q_model_RL
from app.renew_model import DDPG

# общие билиотеки
from tabulate import tabulate
import pandas as pd
import numpy as np
import time
from datetime import datetime

# библиотека записи логов
import logging

# конфигурирование и создание экземпляра логгера
logging.basicConfig(level=logging.INFO, filename='heatRL.log', format='%(asctime)s %(levelname)s:%(message)s',
                    filemode='a')
logger = logging.getLogger(__name__)

# импорт фреймоврка для работы нейросетевых моделей
import torch
import torch.optim as optim

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# оснвная функция обновления модели на накопленном в фале experienceRL.csv опыте
def renew_model_job(df):
    # загружаем в импортированные пустые модели веса из обученных моделей
    p_model_RL.load_state_dict(
        torch.load('./app/model/p_modelRL_M63_v2.pt', map_location=torch.device(DEVICE)))
    q_model_RL.load_state_dict(
        torch.load('./app/model/v_modelRL_M63_v2.pt', map_location=torch.device(DEVICE)))

    # замораживаем часть слоев нейросетей
    for idx, named_param in enumerate(p_model_RL.named_parameters()):
        if idx < 6:
            named_param[1].requires_grad = False
        else:
            named_param[1].requires_grad = True

    for idx, named_param in enumerate(q_model_RL.named_parameters()):
        if idx < 6:
            named_param[1].requires_grad = False
        else:
            named_param[1].requires_grad = True

    # создаем словарь аргументов для экземпляра класса обновления моделей (агент) DDPG
    model_train_dict = dict(policy_model=p_model_RL,
                            policy_max_grad_norm=float('inf'),
                            policy_optimizer_fn=lambda net, lr: optim.RMSprop(net.parameters(), lr=lr, alpha=0.7),
                            policy_optimizer_lr=0.0005,
                            policy_optim_scheduler=lambda optimizer: optim.lr_scheduler.ExponentialLR(optimizer,
                                                                                                      gamma=0.998),
                            value_model=q_model_RL,
                            value_max_grad_norm=float('inf'),
                            value_optimizer_fn=lambda net, lr: optim.RMSprop(net.parameters(), lr=lr, alpha=0.7),
                            value_optimizer_lr=0.0005,
                            value_optim_scheduler=lambda optimizer: optim.lr_scheduler.ExponentialLR(optimizer,
                                                                                                     gamma=0.995),
                            update_target_every_steps=5,
                            tau=0.001,
                            df=df)

    # создаем словарь аргументов для функции тренировки агента класса DDPG
    train_dict = dict(seed=12, gamma=0.7, max_episodes=1)

    # передаем словари аргументов в DDPG для создания агента и аргументов для обновления модели и тренируем агента
    agent = DDPG(**model_train_dict)
    agent.train(**train_dict)

    # записываем средние потери, полученные в ходе тренировки
    p_l = round(sum(agent.p_loss) / len(agent.p_loss), 1)
    v_l = round(sum(agent.v_loss) / len(agent.v_loss), 1)

    # сохраняем веса дообученных на полученном опыте моделей для дальнейшего использования
    torch.save(agent.online_policy_model.state_dict(), './app/model/p_modelRL_M63_v2.pt')
    torch.save(agent.online_value_model.state_dict(), './app/model/v_modelRL_M63_v2.pt')

    print('Successfuly renewed, mean p_loss: {}, mean v_loss: {}'.format(p_l, v_l))
    return 'p_loss: {}, v_loss: {}'.format(p_l, v_l)


def next_temp(state, Theat):
    betta = 1 + (state[4] + state[5] + state[3] / 5) / 3
    toutside = (state[1] + state[2]) / 2
    tinside = state[0]
    Q = (Theat - 33) / 120
    t = toutside + Q / 0.007 + (tinside - toutside - Q / 0.007) / (np.exp(forecast_hours * betta / 70))
    return t

# основная функция получения дейтствия, предлагаемого моделью (устанвка температуры подачи теплоносителя)
# и сохранения полученного опыта 1 раз в 3 часа
def job(url):
    # загружаем данные опыта из папки data
    experience_dataframe = pd.read_csv('./data/experience_RL.csv')
    # загружаем температуру воздуха внутри помещения, полученную из SCADA
    input_df = pd.read_csv('./data/input_data_RL.csv')
    # сохраняем температуру теплоносителя для передачи в SCADA
    output_df = pd.read_csv('./data/output_data_RL.csv')
    # загружаем модель выбора температуры теплоносителя по текущему состоянию
    p_model_RL.load_state_dict(
        torch.load('./app/model/p_modelRL_M63_v2.pt', map_location=torch.device(DEVICE)))
    p_model_RL.eval()

    # устанавливаем значения для переменных текущей целевой температуры в помещении и целевой температуры воздуха
    # через 3 часа для дневного и ночного периодов
    if daytime_span[0] <= datetime.now().hour <= daytime_span[1]:
        ttarget_current = daytime_temperature_target
    else:
        ttarget_current = nighttime_temperature_target

    if daytime_span[0] <= datetime.now().hour + forecast_hours <= daytime_span[1]:
        ttarget_next = daytime_temperature_target
    else:
        ttarget_next = nighttime_temperature_target

    # получаем данные с сайта rp5.ru
    temperature_current, temperature_next, wind, humidity, cloudiness = get_temperatures_forecast(url)
    # получаем температуру воздуха внутри помещения
    Tin_current = input_df['Tinside'].values[0]

    # определяем текущее состояние: список из семи значений (температура внутри помещения, температуры на улице текущая
    # и через 3 часа, ветер, влажность, облачность и целевые температуры воздуха внутри здания текущая и через 3 часа
    state_current = [Tin_current, temperature_current, temperature_next, wind, humidity, cloudiness,
                     ttarget_current, ttarget_next]
    # определяем награду модели за выбранное действие (отклонение факта температуры в помещении от целевой температуры)
    reward = -abs(Tin_current - ttarget_current)
    # с помощью модели определяем действие (температуру теплоносителя для SCADA) на ближайшие 3 часа
    action = round(eval_strat.select_action(p_model_RL, state_current), 1)
    # формируем пустой список для следующего состояния, которое аполним через 3 часа
    state_next = [0.0 for i in range(len(state_current) + 1)]

    state_next[1] = next_temp(state_current, action)
    input_df.loc[0, 'Tinside'] = round(state_next[1], 1)
    input_df.to_csv('./data/input_data_RL.csv', index=False)
    # определяем текущую дату и время для записи опыта
    date = datetime.strftime(datetime.now(), '%d.%m.%y %H:00')

    # записыввем действие в файл для передачи его в SCADA
    output_df.loc[0, 'Theat'] = action
    output_df.to_csv('./data/output_data_RL.csv', index=False)

    # записываем полученный опыт (текущее состояние, награду, выбранное действие и следующее состояние) в файл опыта
    experience_dataframe.loc[
        len(experience_dataframe.index) - 1, ['Reward', 'Tinside_n', 'Toutside_n', 'Toutside_n2', 'W_n', 'Hd_n',
                                                  'Cl_n', 'Ttarget_current_n', 'Ttarget_next_n']] = \
        [reward] + state_current
    experience_dataframe.loc[len(experience_dataframe.index)] = [date] + state_current + [action] + state_next
    experience_dataframe.to_csv('./data/experience_RL.csv', index=False)

    # для информации выводим в виде таблицы текущее состояние и предложенное моделью действие в этом состоянии
    data = [state_current + [round(action, 1)] + [reward]]
    headers = ['Tвн', 'Tнар', 'Тнар_сл', 'W', 'Hd', 'Cl', 'Target', 'Target_next', 'Tпод', 'reward']
    print(tabulate(data, headers=headers))

    # данные для логов
    logs = dict(Tвн=state_current[0], Tнар=state_current[1], Тнар_сл=state_current[2], W=state_current[3],
                Hd=state_current[4], Cl=state_current[5], Target=state_current[6], Target_next=state_current[7],
                Tпод=round(action, 1), Reward= reward)
    return logs


# запуск программы
if __name__ == '__main__':
    while datetime.now() < datetime(2024, 3, 31, 23, 0):
        try:
            logs_dict = job(url_msk)
            experience_df = pd.read_csv('./data/experience_RL.csv')
            experience_df = experience_df[1:-1]
            if len(experience_df[1:-1]) > batch_size:
                renew_result_losses = renew_model_job(experience_df)
                logger.info('%s results of RL model updating', renew_result_losses)
            if logs_dict['Reward'] < -2.0:
                logger.warning('%s REWARD exceeded target temperature more than 2 degrees!', logs_dict)
                print('Warning raised see logs, please!')
        except Exception as e:
            logger.error("Error logged:", exc_info=True)
            print('Error raised see logs, please!')
            pass
        time.sleep(modeling_period*60)
