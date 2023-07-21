import app
from app import pictures, FILTER_THRESHOLD

import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader
	

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
	
	#создаем кнопку logout
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    
    #пишем заголовок приложения на первой странице
    st.markdown("<h1 style='text-align: center; color: darkblue;'>Поиск разности картинок</h1>", unsafe_allow_html=True)
    
    #формируем сбоку инструкцию работы приложения
    pictures.sidebar()
    
    #выбираем тип файла
    file_option = st.selectbox('Выберите тип загружаемых файлов', ('pdf', 'jpg', 'png', 'jpeg'))
    st.write('Вы выбрали:', file_option)
    
    #запускаем основной код сравнения картинок
    pictures.main(file_option, FILTER_THRESHOLD)
    
    #создаем кнопку закрытия приложения
    pictures.exit_app()
   
elif authentication_status is False:
    st.error('Username/password is incorrect')
    
elif authentication_status is None:
    st.warning('Please enter your username and password')
