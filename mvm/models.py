from datetime import datetime
from mvm import db, loginmanager
from flask_login import UserMixin

@loginmanager.user_loader
def loaduser(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    items = db.relationship('Item', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    itemname = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(20), nullable=False, default='default.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Item('{self.item_file}','{self.itemname}', '{self.thumbnail}','{self.date_posted}')"