
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from mvm.config import Config
from flask_babel import Babel
import boto3



mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
babel = Babel()
loginmanager = LoginManager()
loginmanager.login_view ='users.login'
loginmanager.login_message = 'info'

rekognition = boto3.client('rekognition', region_name='eu-central-1')



def create_app(config_class=Config):
    application = Flask(__name__)
    application.config.from_object(Config)
    
    mail.init_app(application)
    db.init_app(application)
    bcrypt.init_app(application)
    babel.init_app(application)
    loginmanager.init_app(application)
    
    from mvm.users.routes import users
    from mvm.items.routes import items
    from mvm.main.routes import main 
    from mvm.errors.handlers import errors
    from mvm.analytics.routes import analytics
    
    application.register_blueprint(users)
    application.register_blueprint(items)
    application.register_blueprint(main)
    application.register_blueprint(errors)
    application.register_blueprint(analytics)
    
    return application

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'].keys())