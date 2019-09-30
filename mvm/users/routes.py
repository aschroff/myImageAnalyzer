from flask import Blueprint, current_app
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from mvm import db, bcrypt
from mvm.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from mvm.models import User, Item
from mvm.users.utils import save_picture, send_reset_email
from flask_babel import gettext
from mvm.analytics.forms import SearchItemForm



users = Blueprint('users', __name__)



@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashedpassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashedpassword)
        db.session.add(user)
        db.session.commit()
        current_app.logger.info('New user registered {} {}'.format(user.username, user.email))  
        flash(gettext('Your account has been created! you are able to log in'), 'success')
        return redirect(url_for('users.login'))
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('register.html', title='Register', form=form, itemsall=itemsall, searchform=searchform)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:     
            current_app.logger.warning('Unsuccessful login attempt {} {}'.format(user.username, user.email))  
            flash(gettext('Login Unsuccessful. Please check email and password'), 'danger')
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('login.html', title='Login', form=form, itemsall=itemsall, searchform=searchform)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
           picturefile = save_picture(form.picture.data) 
           current_user.image_file = picturefile
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(gettext('Your account has been updated!'), 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    imagefile = url_for('static', filename='images/profile_pics/' + current_user.image_file)
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('account.html', title='Account', imagefile=imagefile, form=form, itemsall=itemsall, searchform=searchform)

    

@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form=RequestResetForm()
    if form.validate_on_submit():
       user = User.query.filter_by(email=form.email.data).first()
       send_reset_email(user)
       flash(gettext('An email has been sent with instructions to reset your password.'), 'info')
       return redirect(url_for('users.login'))
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()    
    return render_template('reset_request.html', title='Reset Password', form=form, itemsall=itemsall, searchform=searchform)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash(gettext('That is an invalid or expired token'), "warning")
        return redirect(url_for('users.reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashedpassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashedpassword
        db.session.commit()
        flash(f'Your password has been updated! you are able to log in', 'success')
        return redirect(url_for('users.login'))
    itemsall = Item.query.order_by(Item.date_posted.desc()).all()
    searchform = SearchItemForm()
    return render_template('reset_token.html', title='Reset Password', form=form, itemsall=itemsall, searchform=searchform)