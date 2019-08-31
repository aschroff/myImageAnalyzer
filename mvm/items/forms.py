from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, IntegerField

from wtforms.validators import DataRequired, Length, NumberRange
from flask_babel import lazy_gettext

class CreateItemForm(FlaskForm):
    item_file = FileField(lazy_gettext('Item file'), validators=[FileAllowed(['jpg', 'png'])])
    itemname = StringField(lazy_gettext('Name for item'), validators=[DataRequired(), Length(min=1, max=20)]) 
    analysis_keywords = BooleanField(lazy_gettext('analysis of keywords'))
    analysis_persons = BooleanField(lazy_gettext('analysis of persons'))
    analysis_celebs = BooleanField(lazy_gettext('analysis of celebs'))
    analysis_targets = BooleanField(lazy_gettext('analysis of targets'))
    analysis_text = BooleanField(lazy_gettext('analysis of text'))
    analysis_labels = BooleanField(lazy_gettext('analysis of labels'))
    analysis_keywords_theshold = IntegerField(lazy_gettext('threshold for keyword analysis'), validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField(lazy_gettext('Upload'))