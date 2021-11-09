"""
==================== DATABASE MODELS ====================
This file defines the models for all of the tables in the database.
Prior to importing this file anywhere in the application, `database.init()` must have already been called.
"""

from database.database import DatabaseException
from datetime import datetime
import builtins
from flask_login import UserMixin

db = builtins.piecemeal_db_obj.get_db_obj()

if db == None:
    raise DatabaseException("Database has not been initialized")


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.String(255), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    profile_image = db.Column(db.Text, default="/static/default_user_profile_image.png")

    def to_json(self):
        """
        Returns this table as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "creation_date": self.creation_date,
            "profile_image": self.profile_image,
        }


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))

    def to_json(self):
        """
        Returns this table as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {"id": self.id, "name": self.name, "image": self.image}


class Ingredient(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))

    def to_json(self):
        """
        Returns this table as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {"id": self.id, "name": self.name, "image": self.image}


class SavedRecipe(db.Model):
    __tablename__ = "saved_recipes"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"), nullable=False)

    def to_json(self):
        """
        Returns this table as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {"id": self.id, "user_id": self.user_id, "recipe_id": self.recipe_id}


class SavedIngredient(db.Model):
    __tablename__ = "saved_ingredients"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredients.id"), nullable=False
    )

    def to_json(self):
        """
        Returns this table as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {
            "id": self.id,
            "user_id": self.name,
            "ingredient_id": self.ingredient_id,
        }


class Intolerance(db.Model):
    __tablename__ = "intolerances"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    intolerance = db.Column(db.String(50), nullable=False)

    def to_json(self):
        """
        Returns this table as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {"id": self.id, "user_id": self.user_id, "intolerance": self.intolerance}
