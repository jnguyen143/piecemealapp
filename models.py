from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer)
    username = db.Column(db.String(80))
    email = db.Column(db.String(80))
    profile_pic = db.Column(db.String(100))


db.create_all()
