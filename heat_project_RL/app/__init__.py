#import app.parsing
from datetime import datetime
import pandas as pd

bounds = (30,90)
current_hour = datetime.now().hour + 3

# начальная внутренняя температура
inputs = pd.read_csv('./input/input_data_RL.csv', encoding='cp1251')
tin = inputs['tвнутр'].values[0]

