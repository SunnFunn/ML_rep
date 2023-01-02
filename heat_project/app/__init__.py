import app.parsing
import app.optimizer

import numpy as np
import pandas as pd
from datetime import timedelta
from datetime import datetime

#Глобальные переменные, доступные для всех моддулей
#характеристика здания (цех 15-1 УЗХМ)
qV = 0.1133

# количество часов, необходимое зданию для остывания в e раз (2,71 раз)
gamma = 40

# промежуточные расчетные коэффициенты
alpha = np.round(np.exp(-1/gamma),4)
betta = np.round((1 - alpha)/qV,4)

# нижняя граница внутренней температуры в здании
tmin1 = 16.5
tmin2 = 14.5

# начальная внутренняя температура
inputs = pd.read_csv('C:/Users/Алексей Третьяков/Desktop/ML_rep/heat_project/input/input_data.csv', encoding='cp1251')
t0 = inputs['tвнутр'].values[0]

# ограничения на минимальный и максимальный уровень подачи тепла
Qmin = 0.5
Qmax_heat = np.array([2.98, 2.98, 2.98, 2.98, 2.98, 2.98, 2.98, 3.1, 3.35, 3.53, 3.65, 3.84, 4.03, 4.21, 4.33, 4.52, 4.72, 4.91, 5.1, 5.23, 5.43, 5.62, 5.82, 5.92, 6.15, 6.34, 6.34, 6.34, 6.34, 6.34, 6.34, 6.34, 6.34, 6.34])

#количество прогнозных часов
forecast_hours = 24

#тэги, айди и классы для парсинга
tags_1 = 'table'
tags_2 = 'td'
tags_3 = 'div'
ids = ['forecastTable_1_3']
classes_1 = ['n underlineRow toplineRow red', 
             'n2 underlineRow toplineRow red',
             'd underlineRow toplineRow red',
             'd2 underlineRow toplineRow red',
             'n underlineRow toplineRow blue',
             'n2 underlineRow toplineRow blue',
             'd underlineRow toplineRow blue',
             'd2 underlineRow toplineRow blue']
classes_2 = 't_0'

# генерация часового ряда прогнозного периода
hours = [(datetime.today() + timedelta(hours=x)).hour for x in range(forecast_hours)]
