from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mvm import db, loginmanager
from flask_login import UserMixin
from flask import current_app


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
    targets = db.relationship('Target', backref='searcher', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):         
         s = Serializer(current_app.config['SECRET_KEY'])       
         try:
             user_id = s.loads(token)['user_id']
         except:
             return None
         return User.query.get(user_id)
     
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    itemname = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(20), nullable=False, default='default.jpg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    analysis_keywords = db.Column(db.Boolean, nullable=False, default=False)
    analysis_persons = db.Column(db.Boolean, nullable=False, default=False)
    analysis_celebs = db.Column(db.Boolean, nullable=False, default=False)
    analysis_targets = db.Column(db.Boolean, nullable=False, default=False)
    analysis_text = db.Column(db.Boolean, nullable=False, default=False)
    analysis_labels = db.Column(db.Boolean, nullable=False, default=False)
    analysis_keywords_theshold = db.Column(db.Integer, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    itemkeywords = db.relationship('ItemKeyword', backref='itemin', lazy=True, cascade="delete")
    persons = db.relationship('Person', backref='itemin', lazy=True, cascade="delete")
    def __repr__(self):
        return f"Item('{self.item_file}','{self.itemname}', '{self.thumbnail}','{self.date_posted}')"
    

class ItemKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_analysis = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'), nullable=False)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keyword.id', ondelete='CASCADE'), nullable=False)
    def __repr__(self):
        return f"ItemKeyword('{self.date_analysis, self.item_id, self.keyword_id}')"
    
class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keywordtextname = db.Column(db.String(100), nullable=False)
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    itemkeywords = db.relationship('ItemKeyword', backref='reference', lazy=True)
    def __repr__(self):
        return f"Keyword('{self.keywordtextname}','{self.date_create}')"
    
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_analysis = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    celebrity_id = db.Column(db.Integer, db.ForeignKey('celebrity.id'))
    targetimage_id = db.Column(db.Integer, db.ForeignKey('targetimage.id'))
    personattributes = db.relationship('PersonAttribute', backref='referenceperson', lazy=True, cascade="all, delete-orphan")
    BoundingBoxWidth = db.Column(db.Numeric(precision = 18, scale = 17), nullable=False, default = 1)
    BoundingBoxHeight = db.Column(db.Numeric(precision = 18, scale = 17), nullable=False, default = 1)
    BoundingBoxLeft = db.Column(db.Numeric(precision = 18, scale = 17), nullable=False, default = 0)
    BoundingBoxTop = db.Column(db.Numeric(precision = 18, scale = 17), nullable=False, default = 0)
    AgeLow = db.Column(db.Integer, nullable=False, default=0)
    AgeHigh = db.Column(db.Integer, nullable=False, default=999)
    def __repr__(self):
        return f"Person('{self.date_analysis, self.item_id}')"  
    
class Attribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attributetextname = db.Column(db.String(100), nullable=False)
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    personattributes = db.relationship('PersonAttribute', backref='referenceattribute', lazy=True)
    def __repr__(self):
        return f"Attribute('{self.attributetextname}','{self.date_create}')"
    
class PersonAttribute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_analysis = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'), nullable=False)
    attribute_id = db.Column(db.Integer, db.ForeignKey('attribute.id', ondelete='CASCADE'), nullable=False)
    def __repr__(self):
        return f"PersonAttribute('{self.date_analysis, self.person_id, self.attribute_id}')"  
    
class Celebrity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    aws_id = db.Column(db.String(20), nullable=False)
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    persons = db.relationship('Person', backref='relatedcelebrity', lazy=True)
    def __repr__(self):
        return f"Attribute('{self.name}','{self.date_create}')"    
    
class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    targetimages = db.relationship('Targetimage', backref='imagefortarget', lazy=True, cascade="delete")
    def __repr__(self):
        return f"Target({self.name}'','{self.date_created}')"
        
class Targetimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    target_id = db.Column(db.Integer, db.ForeignKey('target.id'), nullable=False)
    file = db.Column(db.String(20), nullable=False, default='default.jpg')
    name = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(20), nullable=False, default='default.jpg')
    age = db.Column(db.Integer, nullable=False, default=999)
    persons = db.relationship('Person', backref='foundtargetimage', lazy=True)
    
    def __repr__(self):
        return f"Targetimage('{self.date_created, self.target_id, self.name}')"     