from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flask_bootstrap import Bootstrap5

app = Flask(__name__)
app.debug = False
app.config.from_object(Config)

login = LoginManager(app)
login.login_view = 'login'
login.login_message = u"Пожалуйста, авторизуйтесь!"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

assert isinstance(app, object)
bootstrap = Bootstrap5(app)

from app import routes, models
