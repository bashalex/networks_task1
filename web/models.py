import datetime
from app import db
from utils import hash_password


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, password, hash_type='sha256'):
        self.username = username
        self.password = hash_password(password, hash_type)
        self.registration_date = datetime.datetime.now()


class Session(db.Model):

    __tablename__ = 'sessions'

    _id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    username = db.Column(db.String, nullable=False)

    def __init__(self, username, id):
        self.id = id
        self.username = username
