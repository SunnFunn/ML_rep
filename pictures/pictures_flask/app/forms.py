from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, MultipleFileField, \
    TextAreaField, DecimalField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileRequired, FileAllowed

from PIL import ImageFilter

import sqlalchemy as sa
from app import db
from app.db_tables import User

class UploadForm(FlaskForm):
    #files = MultipleFileField('file', validators=[FileAllowed(['pdf'])])
    files = MultipleFileField('file', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Сравнить документы')


class SettingForm(FlaskForm):
    select_thresh = DecimalField('Порог энкодера', validators=[DataRequired()])
    select_kernel_w = IntegerField('Ширина ядра размытия', validators=[DataRequired()])
    select_kernel_h = IntegerField('Высота ядра размытия', validators=[DataRequired()])
    select_iterations = IntegerField('Количество итераций размытия контуров', validators=[DataRequired()])
    select_filter = SelectField('Фильтр')
    select_blend = DecimalField('Затененность фонового документа', validators=[DataRequired()])
    select_dpi = DecimalField('Качество конвертации pdf в jpeg в dpi', validators=[DataRequired()])
    submit = SubmitField('Применить выбранные параметры')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Авторизоваться')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    city = StringField('Город', validators=[DataRequired()])
    company = StringField('Компания', validators=[DataRequired()])
    profession = StringField('Профессия', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повтор пароля', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другое имя пользователя.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Пожалуйста, используйте другой адрес электронной почты.')
