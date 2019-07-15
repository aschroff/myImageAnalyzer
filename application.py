# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 20:46:04 2019

@author: Andi
"""

from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

application = Flask(__name__)
application.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

posts = [
    {
        'owner': 'AndiSchroff',
        'title': 'video1.mpg',
        'description': 'test video',
        'date_posted': 'July 13, 2019'
    },
    {
        'owner': 'AndiSchroff',
        'title': 'video2.mpg',
        'description': 'test video 2',
        'date_posted': 'July 14, 2019'
    }
]


@application.route("/")
@application.route("/home")
def home():
    return render_template('home.html', posts=posts)


@application.route("/about")
def about():
    return render_template('about.html', title='About')


@application.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@application.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    application.run(debug=True)