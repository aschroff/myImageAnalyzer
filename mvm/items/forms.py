from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_babel import lazy_gettext

class CreateItemForm(FlaskForm):
    item = FileField(lazy_gettext('Item'), validators=[FileAllowed(['jpg', 'png'])])
    itemname = StringField(lazy_gettext('Name for item'), validators=[DataRequired(), Length(min=1, max=20)])
    submit = SubmitField(lazy_gettext('Upload'))