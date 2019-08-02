from mvm.dbconfig import databaseURI

class Config:

    SECRET_KEY = '5791628bb0b13ce0c676dfde280ba245'
    SQLALCHEMY_DATABASE_URI = databaseURI
    MAIL_SERVER = 'smtp.strato.de'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'support@schroffs.de'
    MAIL_PASSWORD = 'KSCole1894#'
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch'
    }
    

