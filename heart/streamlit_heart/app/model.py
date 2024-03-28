import pandas as pd
import numpy as np
import streamlit as st
import pickle

# библиотека для обработки входных данных
from sklearn.preprocessing import LabelEncoder


# функция загрузки базы данных о пациентах
@st.cache_data
def load_data(data):
    data_raw = pd.read_csv(data)
    return data_raw


# функция обработки данных
def preprocessing_data(data):
    data_processed = pd.get_dummies(data, columns=['Sex', 'FastingBS', 'ExerciseAngina'])

    labelencoder = LabelEncoder()
    data_processed['ChestPainType'] = labelencoder.fit_transform(data_processed['ChestPainType'])
    data_processed['RestingECG'] = labelencoder.fit_transform(data_processed['RestingECG'])
    data_processed['ST_Slope'] = labelencoder.fit_transform(data_processed['ST_Slope'])
    return data_processed


# инференс на модели
def inference(data, input_data):
    # задаем явно список численных признаков
    nums = ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak']

    # загружаем из файла pkl нашу прогнозную модель, построенную на ансамбле деревьев
    with open('./app/model/heart.pkl', 'rb') as pkl_file:
        model = pickle.load(pkl_file)

    # делаем кнопку запуска блока расчета прогноза и под нее заводим сам расчет прогноза
    result = st.button('Получить прогноз')
    if result:

        for key, value in input_data.items():
            if key in nums:
                input_data[key] = float(value)

        input_data_df = pd.DataFrame(data=input_data, index=[len(data)])
        data_input = pd.concat([data, input_data_df]).drop(['HeartDisease'], axis=1)

        y_to_pred = preprocessing_data(data_input).loc[len(data_input) - 1].values.reshape(1, 14)
        y_proba = model.predict_proba(y_to_pred)[:, 1]

        if y_proba[0] > 0.5:
            st.write(f'У вас высокий кардиологический риск, вероятность заболевания: {np.round(y_proba[0] * 100)}%')
        elif 0.3 < y_proba[0] <= 0.5:
            st.write(f'У вас средний кардиологический риск, вероятность заболевания: {np.round(y_proba[0] * 100)}%')
        else:
            st.write(f'У вас низкий кардиологический риск, вероятность заболевания: {np.round(y_proba[0] * 100)}%')
