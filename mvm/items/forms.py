from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class CreateItemForm(FlaskForm):
    item = FileField('Item', validators=[FileAllowed(['jpg', 'png'])])
    itemname = StringField('Name for item', validators=[DataRequired(), Length(min=1, max=20)])
    submit = SubmitField('Upload')