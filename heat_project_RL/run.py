import app
from app import current_hour, tin
from app.parsing import get_temperatures_forecast
from app.model_RL import eval_strat, model_RL

import torch
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_RL.load_state_dict(torch.load('./app/model/modelRL_3hours_double_target.pth', map_location=torch.device(DEVICE)))

if current_hour >= 4 and current_hour <= 18:
	ttarget_current = 17.0
else:
	ttarget_current = 14.0

	if current_hour + 3 >= 4 and current_hour +3 <= 18:
		target_next = 17.0
	else:
		target_next = 14.0

def main(tin, ttarget_current, target_next):
	temperature, wind, humidity, cloudiness = get_temperatures_forecast()
	state = [tin,temperature, wind, humidity, cloudiness, ttarget_current, target_next]
	action = eval_strat.select_action(model_RL, state)
	return print(state, round(action,1))

if __name__ == '__main__':
	main(tin, ttarget_current, target_next)
