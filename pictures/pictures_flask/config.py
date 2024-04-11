from PIL import ImageFilter
import os

basedir = os.path.abspath(os.path.dirname(__file__))

THRESH = ----
KERNEL = --------
ITERATIONS = -----------------
IM_FILTER = ---------
BLEND_LEVEL = ---------------
DPI = -------------
IDX1 = ----------------
IDX2 = --------------------

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INPUTS_DEFAULT = [----------------------------------------------------]
    MAX_CONTENT_LENGTH = 100*1024 * 1024
    UPLOAD_EXTENSIONS = ['.pdf']
    ALLOWED_USERS = [------------------------------------------]
