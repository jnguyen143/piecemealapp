"""
==================== DATABASE MODELS ====================
This file defines the models for all of the tables in the database.
Prior to importing this file anywhere in the application, `database.init()` must have already been called.
"""

from sqlalchemy.orm import relationship
from database.database import DatabaseException
from datetime import datetime
from flask_login import UserMixin
import builtins
from flask_login import UserMixin

db = builtins.piecemeal_db_obj.get_db_obj()

if db == None:
    raise DatabaseException("Database has not been initialized")


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.String(255), unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    given_name = db.Column(db.String(255))
    family_name = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    profile_image = db.Column(db.Text, default="/static/default_user_profile_image.png")
    username = db.Column(db.String(50), unique=True, nullable=False)
    authentication = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)

    def to_json(self):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {
            "id": self.id,
            "email": self.email,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "creation_date": self.creation_date,
            "profile_image": self.profile_image,
            "username": self.username,
            "authentication": self.authentication,
            "status": self.status,
        }


class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255))

    def to_json(self):
        """
        Returns this row as a JSON object, where each key corresponds to a column
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
        Returns this row as a JSON object, where each key corresponds to a column
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
    recipe = relationship(Recipe, foreign_keys=[recipe_id])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `recipe_id` key will be replaced with a `recipe` key
            which will map to the actual target object.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"user_id": self.user_id, "recipe_id": self.recipe_id}
        return {"user_id": self.user_id, "recipe": self.recipe.to_json()}


class SavedIngredient(db.Model):
    __tablename__ = "saved_ingredients"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    ingredient_id = db.Column(
        db.Integer, db.ForeignKey("ingredients.id"), nullable=False
    )
    ingredient = relationship(Ingredient, foreign_keys=[ingredient_id])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `ingredient_id` key will be replaced with an `ingredient` key
            which will map to the actual target object.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"user_id": self.user_id, "ingredient_id": self.ingredient_id}
        return {"user_id": self.user_id, "ingredient": self.ingredient.to_json()}


class Intolerance(db.Model):
    __tablename__ = "intolerances"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    intolerance = db.Column(db.String(50), nullable=False)

    def to_json(self):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {"user_id": self.user_id, "intolerance": self.intolerance}


class Relationship(db.Model):
    __tablename__ = "friends"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user1 = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    user2 = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    user1_obj = relationship(User, foreign_keys=[user1])
    user2_obj = relationship(User, foreign_keys=[user2])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `user1` and `user2` keys will map to actual user objects instead of just their IDs.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"user1": self.user1, "user2": self.user2}

        return {"user1": self.user1_obj.to_json(), "user2": self.user2_obj.to_json()}


class Password(db.Model):
    __tablename__ = "passwords"
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey("users.id"), nullable=False)
    phrase = db.Column(db.Text, nullable=False)
    user_obj = relationship(User, foreign_keys=[user_id])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `user_id` key will be replaced with a `user` key which will map to the actual user object instead of just the ID.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"user_id": self.user_id, "phrase": self.phrase}

        return {
            "user": self.user_obj.to_json(),
            "phrase": self.phrase,
        }
