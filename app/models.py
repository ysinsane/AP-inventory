#_*_coding:utf-8_*_
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy.exc import IntegrityError
from random import seed
import forgery_py,random
from datetime import datetime
from flask_login import UserMixin,AnonymousUserMixin
from . import login_manager
from flask import flash,current_app

class Permission:
    CHECK = 0x01 #Can only see specific blade is available or not
    TAKE = 0x02 #Can see all items and their amount, and take the blade
    BORROW = 0x04 #Can borrow the blade out
    ASIST = 0x08 #Can create new items, delete items... in a word, can do everything.
    ADMINISTER = 0x80 # reserved for further needs.

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
        'Checker': (Permission.CHECK, True),
        'User': (Permission.CHECK|Permission.TAKE, False),
        'Borrower':(Permission.CHECK|Permission.TAKE|Permission.BORROW,False),
        'Asist': (Permission.CHECK|Permission.TAKE|Permission.BORROW|Permission.ASIST, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    def can(self, permissions):
        return self.role is not None and \
        (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.username

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['AP_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xF).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser
    
class Item(db.Model):
    __tablename__="items"
    id = db.Column(db.Integer,primary_key=True)
    pn = db.Column(db.String(64),unique=True,index=True)
    spec = db.Column(db.String(64),index=True)
    size = db.Column(db.String(64),index=True)
    stock = db.Column(db.Integer)
    in_store = db.Column(db.Boolean,default=False)
    warn_stock = db.Column(db.Integer,nullable=False,default=9999)
    shelf_life = db.Column(db.Date)
    @staticmethod
    def generate_fake(count=100):
        seed()
        for i in range(count):
            item = Item(pn=forgery_py.lorem_ipsum.word(),
                    spec=forgery_py.internet.user_name(True),
                    size=forgery_py.lorem_ipsum.word(),
                    stock=random.randint(2,9),
                    in_store=bool(random.randint(0,1)),
                    warn_stock=random.randint(3,7),
                    shelf_life=forgery_py.date.date(True))
            db.session.add(item)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    def __str__(self):
        return '<class Item> PN:{0} Spec:{1} Size:{2} Stock:{3} warn_stock:{4}'.format(self.pn,
        self.spec,self.size,self.stock,self.warn_stock)
    __repr__=__str__
    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)
        if self.warn_stock is None:
            self.warn_stock = 9999

class Record(db.Model):
    __tablename__="records"
    id = db.Column(db.Integer,primary_key=True)
    qty = db.Column(db.Integer)
    pn = db.Column(db.String(64),index=True)
    spec = db.Column(db.String(64),index=True)
    size = db.Column(db.String(64),index=True)
    time = db.Column(db.DateTime(),default=datetime.utcnow())
    ap_pic = db.Column(db.String)
    customer = db.Column(db.String)
    lend_pic = db.Column(db.String)
    days = db.Column(db.Integer)
    returned = db.Column(db.Boolean,default=False)
    
    def __str__(self):
        return '<class Record> PN:{0} Spec:{1} Size:{2} QTY:{3} \
        Date:{4} Customer:{5}'.format(self.pn,self.spec,
        self.size,self.qty,self.time,self.customer)
        
    __repr__=__str__