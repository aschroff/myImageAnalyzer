import os
import logging


if 'RDS_HOSTNAME' in os.environ:
  DATABASE = {
    'NAME': os.environ['RDS_DB_NAME'],
    'USER': os.environ['RDS_USERNAME'],
    'PASSWORD': os.environ['RDS_PASSWORD'],
    'HOST': os.environ['RDS_HOSTNAME'],
    'PORT': os.environ['RDS_PORT'],
  }
  databaseURI = 'mysql://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s' % DATABASE
  logfile = '/opt/python/log/mvm.log'
  errorfile = '/opt/python/log/mvmerror.log'
  LOG_LEVEL = logging.WARNING
else:
  databaseURI = 'mysql://root:Welcome1@localhost/mvm'
  logfile = './mvm/log/mvm.log'
  errorfile = './mvm/log/mvmerror.log'
  LOG_LEVEL = logging.INFO

#databaseURI = 'mysql://dbadmin:Welcome1@aa185kmyt8wve44.cu76mq9u5srd.eu-central-1.rds.amazonaws.com/mvm'

# default config
class BaseConfig(object):
    DEBUG = True
    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = databaseURI
    MAIL_SERVER = 'smtp.strato.de'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'support@schroffs.de'
    MAIL_PASSWORD = 'KSCole1894##'
    LOG_FILE = logfile
    ERROR_FILE = errorfile    
    LOG_FORMAT = '%(asctime)s:%(name)s:%(message)s'
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch'}


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Welcome1@localhost/mvmtest'


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG


class ProductionConfig(BaseConfig):
    DEBUG = False
    LOG_LEVEL = logging.ERROR


    

