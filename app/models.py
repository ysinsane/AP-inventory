from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy.exc import IntegrityError
from random import seed
import forgery_py,random
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        user=Role(name='user')
        admin=Role(name='admin')
        db.session.add(user)
        db.seesion.add(admin)
        db.session.commit()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    records = db.relationship('Record', backref='user', lazy='dynamic')
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return '<User %r>' % self.username

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def generate_fake(count=100):
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                    username=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(),
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.first()
    
class Item(db.Model):
    __tablename__="items"
    id = db.Column(db.Integer,primary_key=True)
    pn = db.Column(db.String(64),unique=True,index=True)
    spec = db.Column(db.String(64),index=True)
    size = db.Column(db.String(64),index=True)
    stock = db.Column(db.Integer)
    in_store = db.Column(db.Boolean,default=False)
    warn_stock = db.Column(db.Integer)
    shelf_life = db.Column(db.Date)
    records = db.relationship('Record', backref='item',lazy='dynamic')
    lents = db.relationship('Lent', backref='item',lazy='dynamic')
    @staticmethod
    def generate_fake(count=100):
        seed()
        for i in range(count):
            item = User(pn=forgery_py.lorem_ipsum.word(),
                    spec=forgery_py.internet.user_name(True),
                    size=forgery_py.lorem_ipsum.word(),
                    stock=random.randint(2~9)
                    in_store=bool(random.randint(0,1))
                    warn_stock=random.randint(3,7)
                    shelf_life=forgery_py.date.date(True)
            db.session.add(item)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
class Record(db.Model):
    __tablename__="records"
    id = db.Column(db.Integer,primary_key=True)
    qty = db.Column(db.Integer)
    time = db.Column(db.DateTime,index=true,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    customer_id = db.Column(db.Integer,db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

class Customer(db.Model):
    __tablename__="customers"
    id = db.Column(db.Integer,primary_key=True)
    code = db.Column(db.String(64),index=True)
    short_name = db.Column(db.String(64),index=True)
    records = db.relationship('Record', backref='customer', lazy='dynamic')
    records = db.relationship('Lent', backref='customer', lazy='dynamic')

class Lent(db.Model):
    __tablename__="lents"
    id = db.Column(db.Integer,primary_key=True)
    returned = db.Column(db.Boolean,default=False)
    pic = db.Column(db.String(64))
    items = db.Column(db.Integer, db.ForeignKey('items.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('customers.id'))