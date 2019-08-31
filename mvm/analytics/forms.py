from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_babel import lazy_gettext

class CreateTargetForm(FlaskForm):
    name = StringField(lazy_gettext('Name for target'), validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField(lazy_gettext('Upload'))
    
class CreateTargetImageForm(FlaskForm):
    name = StringField(lazy_gettext('Name for target'), validators=[DataRequired(), Length(min=1, max=100)])
    file = FileField(lazy_gettext('Image to compare'), validators=[FileAllowed(['jpg', 'png'])]) 
    age = IntegerField(lazy_gettext('Age of target at image'), validators=[DataRequired(), NumberRange(min=0, max=200)])
    submit = SubmitField(lazy_gettext('Upload'))    