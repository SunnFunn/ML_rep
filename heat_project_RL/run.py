import app
from app import current_hour, daytime_temperature_target, nighttime_temperature_target, daytime_span
from app.parsing import get_temperatures_forecast
from app.model_RL import eval_strat, model_RL

from tabulate import tabulate
import pandas as pd

import torch
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_RL.load_state_dict(torch.load('./app/model/modelRL_3hours_double_target.pth', map_location=torch.device(DEVICE)))

if current_hour >= daytime_span[0] and current_hour <= daytime_span[1]:
	ttarget_current = daytime_temperature_target
else:
	ttarget_current = nighttime_temperature_target

if current_hour + 3 >= daytime_span[0] and current_hour +3 <= daytime_span[1]:
	target_next = daytime_temperature_target
else:
	target_next = nighttime_temperature_target

experience_df = pd.read_csv('./data/experience.csv', encoding='cp1251', sep=';')
input_df = pd.read_csv('./data/input_data_RL.csv', encoding='cp1251', sep=';')

def main(experience_df, input_df, ttarget_current, target_next):
	temperature, wind, humidity, cloudiness = get_temperatures_forecast()
	Tin_current = input_df['tвнутр'].values[0]

	state_current = [Tin_current,temperature, wind, humidity, cloudiness, ttarget_current, target_next]
	reward = -abs(Tin_current - ttarget_current)
	action = round(eval_strat.select_action(model_RL, state_current), 1)
	state_next = [None for x in range(len(state_current)+1)]

	experience_df.loc[len(experience_df.index)-1, ['reward', 'Tin_next', 'Tout_next', 'W_next', 'Hd_next', 'Cl_next',
												   'Ttarget_n', 'Ttarget_next_n']] = [reward] + state_current
	experience_df.loc[len(experience_df.index)] = state_current + [action] + state_next
	experience_df.to_csv('./data/experience.csv', encoding='cp1251', sep=';', index=False)

	data = [state_current + [round(action, 1)]]
	headers = ['Tвн', 'Tнар', 'W', 'Hd', 'Cl', 'Target', 'Target_next', 'Tпод']
	return print(tabulate(data, headers=headers))

if __name__ == '__main__':
	main(experience_df, input_df, ttarget_current, target_next)
