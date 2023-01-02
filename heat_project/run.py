import app
from app import tags_1, tags_2, tags_3, ids, classes_1, classes_2
from app import tmin1, tmin2, t0, Qmin, Qmax_heat, qV, alpha, betta, hours, forecast_hours
from app import stop_year, stop_month, stop_day

import argparse

import schedule
from datetime import datetime

parser = argparse.ArgumentParser(prog='Heat_optim')
parser.add_argument('stop_hour', type=int, help='час остановки программы')
parser.add_argument('stop_minutes', type=int, help='минуты остановки программы')
#parser.add_argument('t0', type=float, help='Начальная температура воздуха внутри цеха')
args = parser.parse_args()

def job():
	outside_temperature  = app.parsing.get_temperatures_forecast(tags_1,tags_2, tags_3, ids,
	                                                             classes_1, classes_2, forecast_hours)
	Qmax = app.optimizer.Qbounds(outside_temperature, app.optimizer.temps_out, Qmax_heat)
	inputs_to_optimizer = app.optimizer.create_matrix_vectors_bounds(t0, tmin1, tmin2, alpha, betta, Qmin, Qmax,
	                                                                 outside_temperature, hours, forecast_hours)
	Q = app.optimizer.optimize(inputs_to_optimizer[0],
	                           inputs_to_optimizer[1],
	                           inputs_to_optimizer[2],
	                           inputs_to_optimizer[3])
	internal_temp = app.optimizer.internal_temp(t0, alpha, betta, outside_temperature, Q, forecast_hours)
	heat_temp = app.optimizer.heat_temp(qV, tmin1, tmin2, Q, hours, forecast_hours)
	app.optimizer.data(outside_temperature, Q, internal_temp, heat_temp, forecast_hours)

def main(stop_year, stop_month, stop_day, stop_hour, stop_minutes):
	schedule.every(15).minutes.do(job)
	while datetime.now() < datetime(stop_year, stop_month, stop_day, stop_hour, stop_minutes):
		schedule.run_pending()
	

if __name__ == '__main__':
	main(stop_year, stop_month, stop_day, args.stop_hour, args.stop_minutes)
