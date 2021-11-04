"""
==================== DATABASE MODELS ====================
This file defines the models for all of the tables in the database.
Prior to importing this file anywhere in the application, `database.init()` must have already been called.
"""

from database.database import get_database_obj
from datetime import datetime

db = get_database_obj()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(255), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))


class Ingredient(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))


class SavedRecipe(db.Model):
    __tablename__ = "saved_recipes"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)


class SavedIngredient(db.Model):
    __tablename__ = "saved_ingredients"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredients.id"), nullable=False
    )


class Intolerance(db.Model):
    __tablename__ = "intolerances"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    intolerance = db.Column(db.String(50), nullable=False)
