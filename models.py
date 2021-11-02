from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(80))

    def __repr__(self):
        return f"<User {self.username},Email {self.email}>"

    def get_username(self):
        return self.username


class AppUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredients = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"<Ingredients {self.ingredients}>"


db.create_all()
