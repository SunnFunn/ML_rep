from datetime import datetime
from app import db
from flask_login import UserMixin
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    city = db.Column(db.String(64))
    profession = db.Column(db.String(128))
    surnames = db.relationship('Surnames', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Surnames(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname_beginning = db.Column(db.String(140))
    surnames_generated = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Surnames {}>'.format(self.surnames_generated)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
