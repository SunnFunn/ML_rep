from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, MultipleFileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, DataRequired
from flask_wtf.file import FileField, FileRequired

class UploadForm(FlaskForm):
    pictures = MultipleFileField('Выберите два файла с картинками')
    submit = SubmitField('Загрузить файлы')
