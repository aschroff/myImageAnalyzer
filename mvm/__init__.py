
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from mvm.dbconfig import databaseURI
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

application = Flask(__name__)
application.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
application.config['SQLALCHEMY_DATABASE_URI'] = databaseURI
application.config['MAIL_SERVER'] = 'smtp.strato.de'
application.config['MAIL_PORT'] = 465
application.config['MAIL_USE_SSL'] = True
application.config['MAIL_USERNAME'] = 'support@schroffs.de'
application.config['MAIL_PASSWORD'] = 'KSCole1894#'
mail = Mail(application)

db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
loginmanager = LoginManager(application)
loginmanager.login_view ='login'
loginmanager.login_message = 'info'

from mvm import routes