from app import app
from __init__ import FILTER_THRESHOLD

import streamlit as st
import streamlit_authenticator as stauth

import yaml
from yaml.loader import SafeLoader

import time
import keyboard
import os
import psutil
	

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
    authenticator.logout('Logout', 'main', key='unique_key')
    app.sidebar()
    pdf_file_1, pdf_file_2 = app.pdf_uploader()
    im_1, im_2 = app.pdf_converter(pdf_file_1, pdf_file_2)
    diff_inv_red = app.get_pictures_difference(im_1, im_2, FILTER_THRESHOLD)
    result =  app.get_pictures_blend(diff_inv_red, im_2)
    app.result(im_1, im_2)
    app.load_pictures(im_1)
   
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
	
exit_app = st.sidebar.button("Закрыть приложение")
if exit_app:
    # Give a bit of delay for user experience
    time.sleep(2)
    # Close streamlit browser tab
    keyboard.press_and_release('ctrl+w')
    # Terminate streamlit python process
    pid = os.getpid()
    p = psutil.Process(pid)
    p.terminate()
