import app
from app import model, home_page
from app import reference, image, title

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

def main():
	app.home_page.title(title, image)
	app.home_page.sidebar(reference)
	app.home_page.greetings()
	data = app.model.load_data('./app/heart.csv')
	input_data = app.home_page.input_data(data)
	model.inference(data, input_data)

if authentication_status:
	
	#создаем кнопку logout
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    
    #запускаем основной код сравнения картинок
    main()
   
elif authentication_status is False:
    st.error('Username/password is incorrect')
    
elif authentication_status is None:
    st.warning('Please enter your username and password')
