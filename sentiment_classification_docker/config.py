import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    HOST = '0.0.0.0'
    PORT = 5000
    MODEL_LOCATION = './app/model/model.pth'
    DEVICE = 'cpu'
