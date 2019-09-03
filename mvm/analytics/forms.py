from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
from wtforms import StringField, SubmitField, IntegerField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField , QuerySelectMultipleField
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
    
class SearchItemForm(FlaskForm):
    #Text
    searchtext = StringField(lazy_gettext('Text for search'), validators=[Length(min=0, max=100)])
#    search_keywords  = BooleanField(lazy_gettext('search in keywords'))
#    search_attributes = BooleanField(lazy_gettext('search in attributes of persons'))
#    search_celebs = BooleanField(lazy_gettext('search in names of celebtrities'))
#    search_text = BooleanField(lazy_gettext('search in text'))
#    #Age
#    search_age = IntegerField(lazy_gettext('search via age of persons'), validators=[NumberRange(min=0, max=999)])
#    #Targets
#    search_targets = QuerySelectMultipleField(get_label='name', label='Target to search')
    submit = SubmitField(lazy_gettext('Search')) 