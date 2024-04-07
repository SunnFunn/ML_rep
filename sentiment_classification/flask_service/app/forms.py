from flask import flash, url_for,redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import ValidationError, DataRequired
from app.tables import User, Text
from app import db

import sqlalchemy as sa


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


def validate_username(form, username):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    if user is not None:
        flash('This name exist, please, enter another name!')
        return redirect(url_for("register"))
    else:
        user = User(username=form.username.data, city=form.city.data, profession=form.profession.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for("login"))


class DataForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    submit = SubmitField('submit')
