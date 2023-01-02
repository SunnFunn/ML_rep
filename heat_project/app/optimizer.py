import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime

from scipy.optimize import linprog

# формируем массив температур внешнего воздуха в температурном графике поставщика тепла
temps_out = np.zeros(34)
temps_out[0] = 8
for i in range(33):
    temps_out[i+1] = temps_out[i] - 1

# функция формирования массива ограничений сверху на отпуск тепла
def Qbounds(outside_temperature, temps_out, Qmax_heat):
	Qmax = np.zeros(24, dtype=float)
	for i in range(24):
		position = np.where(temps_out == outside_temperature[i])[0].tolist()[0]
		Qmax[i] = Qmax_heat[position]
	Qmax = Qmax.tolist()
	
	return Qmax

# функция создания матрицы и векторов для оптимизации
def create_matrix_vectors_bounds(t0, tmin1, tmin2, alpha, betta, Qmin, Qmax, outside_temperature, hours, forecast_hours):
	c = np.ones(forecast_hours, dtype=int)
	
	A =np.diag(np.full(forecast_hours,-betta))
	for i in range(1,forecast_hours):
		A += np.diag(np.full(forecast_hours-i,-betta*(alpha**i)), -i)
	
	b_1 = np.zeros(forecast_hours)
	b_1[0] = outside_temperature[0]*(1 - alpha)
	for i in range(1,forecast_hours):
		b_1[i] = b_1[i-1] + outside_temperature[i]*(1 - alpha)*alpha**i
	
	b_2 = np.zeros(forecast_hours)
	for i in range(forecast_hours):
		if 19 <= hours[i] <= 24 or 0 <= hours[i] <= 6:
			b_2[i] = -tmin2 + t0*alpha**(i+1)
		else:
			b_2[i] = -tmin1 + t0*alpha**(i+1)
	
	b = np.round(b_1 + b_2, 2)
	
	bounds = []
	for i in range(forecast_hours):
		bounds.append((Qmin, Qmax[i]))
	
	return c, A, b, bounds

# функция оптимизации и расчета прогнозной подачи тепла
def optimize(c, A, b, bounds):
	result = linprog(c, A_ub=A, b_ub=b, bounds=bounds)
	Q = np.round(np.array(result.x),2)
	
	return Q

# функция оценки прогноза температуры внутреннего воздуха
def internal_temp(t0, alpha, betta, outside_temperature, Q, forecast_hours):
	internal_temp = []
	internal_temp.append(t0)
	for i in range(1,forecast_hours):
		ti = internal_temp[i-1]*alpha + Q[i-1]*betta + outside_temperature[i-1]*(1-alpha)
		internal_temp.append(np.round(ti,1))
	
	return internal_temp

# функция оценки прогноза температуры подачи теплоносителя
def heat_temp(qV, tmin1, tmin2, Q, hours, forecast_hours):
	heat_temp = []
	for i in range(forecast_hours):
		if 19 <= hours[i] <= 24 or 0 <= hours[i] <= 6:
			ti = tmin2 + ((115+80)/2 - tmin2)*(Q[i]/(qV*(tmin2+40)))**0.8 + ((115-80)/2)*(Q[i]/(qV*(tmin2+40)))
		else:
			ti = tmin1 + ((115+80)/2 - tmin1)*(Q[i]/(qV*(tmin1+40)))**0.8 + ((115-80)/2)*(Q[i]/(qV*(tmin1+40)))
		heat_temp.append(np.round(ti))
	
	return heat_temp

# функция создания и сохранения таблицы расчетных данных в файле csv
def data(outside_temperature, Q, internal_temp, heat_temp, forecast_hours):
	dates = np.asarray([(datetime.today() + timedelta(hours=x)).strftime('%Y-%m-%d %H') for x in range(forecast_hours)]).reshape(forecast_hours,1)
	out_tem = np.asarray(outside_temperature).reshape(forecast_hours,1)
	Q_Gkal = np.asarray(Q).reshape(forecast_hours,1)
	tpod = np.asarray(heat_temp).reshape(forecast_hours,1)
	tvn = np.asarray(internal_temp).reshape(forecast_hours,1)
	
	data_array = np.hstack((dates, out_tem, Q_Gkal, tpod, tvn))
	cols = ['дата', 'tвнеш', 'Q_Гкал', 'tподающ', 'tвнутр']
	data = pd.DataFrame(data_array, columns=cols)
	base = datetime.today()
	data.to_csv('./output/data_{}_{}_{}_{}_{}.csv'.format(base.year, base.month, base.day, base.hour+3, base.minute), encoding='cp1251', index=False)
