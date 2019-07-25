import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from mvm import application, db, bcrypt, mail
from mvm.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateItemForm, RequestResetForm, ResetPasswordForm
from mvm.models import User, Item
from flask_mail import Message



@application.route("/")
@application.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    items = Item.query.order_by(Item.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template('home.html', items=items)


@application.route("/about")
def about():
    db.drop_all()
    db.create_all()
    
    return render_template('about.html', title='About')


@application.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashedpassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashedpassword)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! you are able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@application.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:       
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@application.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picturefilename = random_hex + f_ext
    picturepath = os.path.join(application.root_path, 'static/images/profile_pics', picturefilename)
    outputsize = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(outputsize)
    i.save(picturepath)
    return picturefilename

@application.route("/account", methods=['GET', 'POST'])
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
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    imagefile = url_for('static', filename='images/profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', imagefile=imagefile, form=form)

def save_thumbnail(form_picture):
    random_hex=secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picturefilename = random_hex + f_ext
    picturepath = os.path.join(application.root_path, 'static/images/thumbnails', picturefilename)
    outputsize = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(outputsize)
    i.save(picturepath)
    return picturefilename

def save_item(form_picture):
    random_hex=secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picturefilename = random_hex + f_ext
    picturepath = os.path.join(application.root_path, 'static/images/items', picturefilename)
    i = Image.open(form_picture)
    i.save(picturepath)
    return picturefilename


@application.route("/item/new", methods=['GET', 'POST'])
@login_required
def new_item():
    form = CreateItemForm()
    if form.validate_on_submit():  
        if form.item.data:
           itemfile = save_item(form.item.data) 
           thumbnailfile = save_thumbnail(form.item.data)  
           print (itemfile, form.itemname.data, thumbnailfile, current_user)          
           item = Item(item_file = itemfile, itemname = form.itemname.data, thumbnail = thumbnailfile, owner = current_user)
           db.session.add(item)
           db.session.commit()
           flash('Your new item has been created', 'success')
           return redirect(url_for('home'))
    return render_template('create_item.html', title='New Item', form=form, legend='New Item')

@application.route("/item/<int:item_id>")
def item(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item.html', title=item.itemname, item=item)   

@application.route("/item/<int:item_id>/update", methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    print('a')
    if item.owner != current_user:
        abort(403)
    form=CreateItemForm()
    print('b')
    if form.validate_on_submit():
        print('c')
        if form.item.data:
           print('d')
           item.item_file = save_item(form.item.data) 
           item.thumbnail = save_thumbnail(form.item.data)           
           item.itemname = form.itemname.data
           db.session.commit()
           flash('Your item has been updated', 'success')
           return redirect(url_for('item', item_id=item.id))   
        elif form.itemname.data != item.itemname:
           item.itemname = form.itemname.data
           db.session.commit()
           flash('Your item has been updated1', 'success')
           return redirect(url_for('item', item_id=item.id))  
    elif request.method == 'GET':
        form.itemname.data = item.itemname
    return render_template('create_item.html', title="Update Item",
                           form=form, legend='Update Item', item=item)  
    
@application.route("/item/<int:item_id>/delete", methods=['POST'])
@login_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner != current_user:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Your item has been deleted', 'success')
    return redirect(url_for('home'))


@application.route("/user/<string:username>")
def user_items(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    items = Item.query.filter_by(owner=user).order_by(Item.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template('user_items.html', items=items, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='support@schroffs.de', recipients=[user.email])
    msg.body = f'''To reset your passowrd, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes are needed.
'''
    mail.send(msg)
    

@application.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
       user = User.query.filter_by(email=form.email.data).first()
       send_reset_email(user)
       flash('An email has been sent with instructions to reset your password.', 'info')
       return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@application.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', "warning")
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashedpassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashedpassword
        db.session.commit()
        flash(f'Your password has been updated! you are able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)