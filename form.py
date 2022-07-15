#! python3

from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms_components import TimeField
from wtforms.validators import DataRequired

class AlarmForm(FlaskForm):
    time =  TimeField('Alarm Time', [DataRequired()])
    submit = SubmitField('Submit')