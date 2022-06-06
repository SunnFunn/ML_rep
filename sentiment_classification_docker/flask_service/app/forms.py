from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import ValidationError, DataRequired
from app.tables import User, Text

class InputForm(FlaskForm):
    input_text = StringField(validators=[DataRequired()])
    submit = SubmitField('submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    city = StringField('Your city', validators=[DataRequired()])
    profession = StringField('Profession', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class DataForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    submit = SubmitField('submit')
