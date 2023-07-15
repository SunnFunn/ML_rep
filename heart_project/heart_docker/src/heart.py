import pandas as pd
import numpy as np
import streamlit as st
import pickle

#библиотека для моделирования
from sklearn.ensemble import ExtraTreesClassifier

#библиотека для обработки входных данных
from sklearn.preprocessing import LabelEncoder

#пишем зашоловок и оформляем страницу тематической картинкой
st.title("Прогноз риска кардиологического заболевания человека")
st.image('https://images.24ur.com/media/images/1024x576/May2017/e5b28ffeb0_61920351.jpg?v=d41d')

#загружаем датафрейм базу данных о пациентах
@st.cache_data
def load_data(data):
	data_raw = pd.read_csv(data)
	return data_raw

def preprocessing_data(data):
	
	data_processed = pd.get_dummies(data, columns = ['Sex', 'FastingBS', 'ExerciseAngina'])
	
	labelencoder = LabelEncoder()
	
	data_processed['ChestPainType'] = labelencoder.fit_transform(data_processed['ChestPainType'])
	data_processed['RestingECG'] = labelencoder.fit_transform(data_processed['RestingECG'])
	data_processed['ST_Slope'] = labelencoder.fit_transform(data_processed['ST_Slope'])
	return data_processed

hr = load_data('heart.csv')

#вспомогательные списки названий признаков
cols = hr.columns
nums = ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak']
cats = ['Sex','ChestPainType','RestingECG', 'ExerciseAngina','ST_Slope']

#загружаем из файла pkl нашу прогнозную модель, построенную на ансамбле деревьев
with open('heart.pkl', 'rb') as pkl_file:
    model = pickle.load(pkl_file)

#делаем справочную информацию о данных, которые необходимо ввести для прогноза
reference = {'Age': 'Ваш возраст',
'Sex':'Ваш пол',
'ChestPainType':'Тип боли в грудной клетке',
'RestingBP':'Давление крови в покое',
'Cholesterol':'Уровень общего холестерина в крови',
'FastingBS':'Уровень сахара в крови натощак (1, если больше 6,6 мммоль/л и 0 в остальных случаях',
'RestingECG':'результат кардиограммы в покое',
'MaxHR':'максимально достижимый уровень пульса',
'ExerciseAngina':'наличие боли в грудной клетке при физической нагрузке',
'Oldpeak':'oldpeak = ST (Numeric value measured in depression)',
'ST_Slope':'the slope of the peak exercise ST segment (Up: upsloping, Flat: flat, Down: downsloping)'}

#выводим справочную информацию о значениях и диапазонах входных данных на боковую панель
st.sidebar.markdown('**Словарь данных о пациентах:**')
for key,value in reference.items():
    st.sidebar.markdown(f'**{key}**: {value}')

#Приветствие и небольшая инструкция к заполнению входных данных
st.markdown('**Здравствуйте, необходимо ввести свои медцинские данные для оценки риска кардиологического заболевания.**')
st.markdown('```В случае возникновения вопросов с введением данных пользуйтесь справочником на панели слева.```')

#формируем словарь с входными данными через диалоговые окна и бегунки
input_data = {}
for col in hr.columns[:-1]:
	if col in nums:
		st.subheader(f'Выберете ваши данные {col}')
		col_range = range(int(hr[col].min()),int(hr[col].max()))
		input_data[col] = st.select_slider('выберете значение из диапазона', options=col_range, value=int(hr[col].mean()))
	elif col == 'FastingBS':
		st.subheader(f'Выберете ваши данные {col}')
		input_data[col] = st.selectbox('выберете значение из списка', [0,1])
	else:
		st.subheader(f'Выберете ваши данные {col}')
		input_data[col] = st.selectbox('выберете значение из списка', hr[col].unique())
		
#делаем кнопку запуска блока расчета прогноза и под нее заводим сам расчет прогноза
result = st.button('Получить прогноз')
if result:
	
	for key,value in input_data.items():
		if key in nums:
			input_data[key] = float(value)
	
	input_data_df = pd.DataFrame(data=input_data, index=[len(hr)])
	hr_input = hr.append(input_data_df).drop(['HeartDisease'], axis=1)
	
	y_to_pred = preprocessing_data(hr_input).loc[len(hr_input) - 1].values.reshape(1,14)
	y_proba = model.predict_proba(y_to_pred)[:,1]
	if y_proba[0] > 0.5:
		st.write(f'У вас высокий кардиологический риск, вероятность заболевания: {np.round(y_proba[0]*100)}%')
	elif 0.3 < y_proba[0] <= 0.5:
		st.write(f'У вас средний кардиологический риск, вероятность заболевания: {np.round(y_proba[0]*100)}%')
	else:
		st.write(f'У вас низкий кардиологический риск, вероятность заболевания: {np.round(y_proba[0]*100)}%')

