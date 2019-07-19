
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from mvm.dbconfig import databaseURI
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

application = Flask(__name__)
application.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
application.config['SQLALCHEMY_DATABASE_URI'] = databaseURI

db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
loginmanager = LoginManager(application)
loginmanager.login_view ='login'
loginmanager.login_message = 'info'

from mvm import routes