from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, InputRequired


def query_length_check(form, field):
    if len(field.data.split(' ')) > 200:
        raise ValidationError('Field must be less than 200 tokens')


class QueryForm(FlaskForm):
    query = TextAreaField('', validators=[DataRequired(), InputRequired(), query_length_check])
    submit = SubmitField('Get AI model answer')
