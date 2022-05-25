from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class StringForm(FlaskForm):
    input_text = StringField('in this field', validators=[DataRequired()])
    submit = SubmitField('submit text')
