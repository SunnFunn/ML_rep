import streamlit as st
import streamlit_authenticator as stauth

import tempfile
import shutil

#hashed_password = stauth.Hasher(['Qwerty54321']).generate()

dirpath = tempfile.mkdtemp()
print(dirpath)
shutil.rmtree(dirpath)
