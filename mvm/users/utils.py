import os
import secrets
from PIL import Image
from flask import url_for, current_app
from mvm import mail
from flask_mail import Message


def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picturefilename = random_hex + f_ext
    picturepath = os.path.join(current_app.root_path, 'static/images/profile_pics', picturefilename)
    outputsize = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(outputsize)
    i.save(picturepath)
    return picturefilename

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='support@schroffs.de', recipients=[user.email])
    msg.body = f'''To reset your passowrd, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes are needed.
'''
    mail.send(msg)