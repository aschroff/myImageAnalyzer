from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from mvm.models import User
from flask_babel import lazy_gettext


class RegistrationForm(FlaskForm):
    username = StringField(lazy_gettext('Username'),
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(lazy_gettext('Email'),
                        validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    confirm_password = PasswordField(lazy_gettext('Confirm Password'),
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(lazy_gettext('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(lazy_gettext('That username is taken. Please choose a different one.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(lazy_gettext('That email is taken. Please choose a different one.'))
        

class LoginForm(FlaskForm):
    email = StringField(lazy_gettext('Email'),
                        validators=[DataRequired(), Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
    remember = BooleanField(lazy_gettext('Remember Me'))
    submit = SubmitField(lazy_gettext('Login'))

class UpdateAccountForm(FlaskForm):
    username = StringField(lazy_gettext('Username'),
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(lazy_gettext('Email'),
                        validators=[DataRequired(), Email()])
    picture = FileField(lazy_gettext('Profile Picture'), validators=[FileAllowed(['jpg', 'png'])])        
    submit = SubmitField(lazy_gettext('Update'))

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(lazy_gettext('That username is taken. Please choose a different one.'))

    def validate_email(self, email):
        if email.data != current_user.email:        
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(lazy_gettext('That email is taken. Please choose a different one.'))
                

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])  
    submit = SubmitField('Update')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(lazy_gettext('There is no account with this email. PLease register first.'))
            
class ResetPasswordForm(FlaskForm):
        password = PasswordField(lazy_gettext('Password'), validators=[DataRequired()])
        confirm_password = PasswordField(lazy_gettext('Confirm Password'), validators=[DataRequired(), EqualTo('password')])
        submit = SubmitField(lazy_gettext('Reset Password'))     