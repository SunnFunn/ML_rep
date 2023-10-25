import app
from app import pictures, settings

import time
import numpy as np

import streamlit as st
import streamlit_authenticator as stauth
from PIL import Image

st.set_page_config(page_title="Сравниваем чертежи и текст",
				  page_icon='icon.png',
				  layout="wide",
				  initial_sidebar_state="collapsed")

tab1, tab2, tab3, tab4 = st.tabs(["Login", "Register", "Main", "Settings"])

import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
	config = yaml.load(file, Loader=SafeLoader)

#if 'authenticator' not in st.session_state:
st.authenticator = stauth.Authenticate(
		config['credentials'],
		config['cookie']['name'],
		config['cookie']['key'],
		config['cookie']['expiry_days'],
		config['preauthorized']
		)

name, authentication_status, username = st.authenticator.login('Login', 'main')

if 'authentication_status' not in st.session_state:
	st.session_state['authentication_status'] = authentication_status

with tab1:
	
	if authentication_status:
		st.write("**Теперь вы можете перейти на основные вкладки приложения и в настройки**")
		with tab3:
			#пишем заголовок приложения на первой странице
			st.markdown("<h1 style='text-align: center; color: darkblue;'>Поиск разности картинок</h1>", unsafe_allow_html=True)
		
			with tab4:
				#создаем кнопку logout
				st.authenticator.logout('Logout', 'main', key='multiple_key')
				#формируем вкладку настройки
				distance_thresh, dpi, kernel, iterations, im_filter, blend_level = settings.settings()
				
			#создаем кнопку logout
			st.authenticator.logout('Logout', 'main', key='unique_key')
		
			#выбираем тип файла
			file_option = st.selectbox('Выберите тип загружаемых файлов', ('pdf', 'jpg', 'png', 'jpeg'))
			st.write('Вы выбрали:', file_option)
		
			#запускаем основной код сравнения картинок
			start = time.time()
			pictures.main(file_option, distance_thresh, dpi, kernel, iterations, im_filter, blend_level)
			end = time.time()
			st.write('Сравнение картинок выполнено за:',np.round((end-start),1), 'сек')
		
	elif authentication_status is False:
		st.error('Username/password is incorrect')
		with tab3:
			st.error('Username/password is incorrect')
		with tab4:
			st.error('Username/password is incorrect')
		
	elif authentication_status is None:
		st.warning('Please enter your username and password or register')
		with tab3:
			st.warning('Please enter your username and password or register')
		with tab4:
			st.warning('Please enter your username and password or register')

with tab2:		
	try:
		if st.authenticator.register_user('Register user', 'main', preauthorization=False):
			with open('config.yaml', 'w') as file:
				yaml.dump(config, file, default_flow_style=False)
			st.success('User registered successfully')
			
	except Exception as e:
		st.error(e)
