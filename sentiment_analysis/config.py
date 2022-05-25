import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MODEL_HOST = 'localhost'
    MODEL_PORT = 5000
    MODEL_LOCATION = 'model.pth'
    DEVICE = 'cpu'
