import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    RESULTED_PICTURES_FOLDER = os.path.join(basedir, 'pictures')
    IMAGES_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
    FILTER_THRESHOLD = 200
