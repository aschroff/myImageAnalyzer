from flask_testing import TestCase

from application import application
from mvm import db, bcrypt
from mvm.models import User, Item
from mvm.config import TestConfig



class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        application.config.from_object(TestConfig)
        return application

    def setUp(self):
        db.create_all()
        hashedpassword = bcrypt.generate_password_hash("admin").decode('utf-8')
        user = User(username="admin", email="ad@min.com", password=hashedpassword)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
