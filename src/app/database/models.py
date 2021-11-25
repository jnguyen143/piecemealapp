"""
==================== DATABASE MODELS ====================
This file defines the models for all of the tables in the database.
Prior to importing this file anywhere in the application,
`database.init()` must have already been called.
"""

# This import works
# pylint: disable=import-error
import builtins
from datetime import datetime
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from .database import DatabaseException

# This member is present
# pylint: disable=no-member
DATABASE = builtins.piecemeal_db_obj.get_db_obj()

if DATABASE is None:
    raise DatabaseException("Database has not been initialized")


class User(DATABASE.Model, UserMixin):
    """
    The users table is responsible for storing user data.
    It keeps track of all users across the site and their
    related account information, such as their IDs, usernames,
    emails, and authentication methods.
    """

    __tablename__ = "users"
    id = DATABASE.Column(
        DATABASE.String(255), unique=True, nullable=False, primary_key=True
    )
    email = DATABASE.Column(DATABASE.String(255), nullable=False)
    given_name = DATABASE.Column(DATABASE.String(255))
    family_name = DATABASE.Column(DATABASE.String(255))
    creation_date = DATABASE.Column(
        DATABASE.DateTime, nullable=False, default=datetime.utcnow
    )
    profile_image = DATABASE.Column(
        DATABASE.Text, default="/static/default_user_profile_image.png"
    )
    username = DATABASE.Column(DATABASE.String(50), unique=True, nullable=False)
    authentication = DATABASE.Column(DATABASE.Integer, nullable=False)
    status = DATABASE.Column(DATABASE.Integer, nullable=False, default=0)

    def to_json(self, shallow: bool = False):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): Whether the returned JSON object should only contain minimal data
                (i.e. no sensitive data, such as email and authentication method).
                This value is false by default.

        Returns:
            This row instance as a JSON object.
        """
        result = {
            "id": self.id,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "profile_image": self.profile_image,
            "username": self.username,
        }

        if not shallow:
            result["email"] = self.email
            result["authentication"] = self.authentication
            result["creation_date"] = self.creation_date
            result["status"] = self.status
            result["display_creation_date"] = self.creation_date.strftime("%d %B, %Y")

        return result


class Recipe(DATABASE.Model):
    """
    The recipes table is responsible for storing global information of recipes
    across the site without reference to any users. This table is designed
    to be used as a central location to retrieve information about recipes
    without having to resort to making calls to 3rd party APIs every time a
    request for recipe information needs to be made.

    Keep in mind this table stores global information.
    This means that it does not store information associated with any particular user.
    For storing recipes with particular users, refer to the `saved_recipes` table.
    """

    __tablename__ = "recipes"
    id = DATABASE.Column(
        DATABASE.Integer, unique=True, nullable=False, primary_key=True
    )
    name = DATABASE.Column(DATABASE.String(255), nullable=False)
    image = DATABASE.Column(DATABASE.String(255))
    summary = DATABASE.Column(DATABASE.Text)
    full_summary = DATABASE.Column(DATABASE.Text)

    def to_json(self):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {
            "id": self.id,
            "name": self.name,
            "image": self.image,
            "summary": "" if self.summary is None else self.summary,
            "full_summary": "" if self.full_summary is None else self.full_summary,
        }


class Ingredient(DATABASE.Model):
    """
    The ingredients table is responsible for storing global information
    of ingredients across the site without reference to any users.
    This table is designed to be used as a central location to retrieve
    information about ingredients without having to resort to making calls
    to 3rd party APIs every time a request for ingredient information needs to be made.

    Keep in mind this table stores global information.
    This means that it does not store information associated with any particular user.
    For storing ingredients with particular users, refer to the `saved_ingredients` table.
    """

    __tablename__ = "ingredients"
    id = DATABASE.Column(
        DATABASE.Integer, unique=True, nullable=False, primary_key=True
    )
    name = DATABASE.Column(DATABASE.String(255), nullable=False)
    image = DATABASE.Column(DATABASE.String(255))

    def to_json(self):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {"id": self.id, "name": self.name, "image": self.image}


class SavedRecipe(DATABASE.Model):
    """
    The saved_recipes table is responsible for storing information
    about a user's saved recipes. This table only stores mappings
    for users to recipes; it does not store actual user or recipe
    information. To retrieve user and recipe information, refer to
    the users and recipes tables, respectively.
    """

    __tablename__ = "saved_recipes"
    id = DATABASE.Column(
        DATABASE.Integer, unique=True, nullable=False, primary_key=True
    )
    user_id = DATABASE.Column(
        DATABASE.String(255),
        DATABASE.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    recipe_id = DATABASE.Column(
        DATABASE.Integer,
        DATABASE.ForeignKey("recipes.id", onupdate="CASCADE", ondelete="NO ACTION"),
        nullable=False,
    )
    recipe = relationship(Recipe, foreign_keys=[recipe_id])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `recipe_id`
                key will be replaced with a `recipe` key
                which will map to the actual target object.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"user_id": self.user_id, "recipe_id": self.recipe_id}
        return {"user_id": self.user_id, "recipe": self.recipe.to_json()}


class SavedIngredient(DATABASE.Model):
    """
    The saved_ingredients table is responsible for storing information
    about a user's saved ingredients. This table only stores mappings
    for users to ingredients; it does not store actual user or ingredient
    information. To retrieve user and ingredient information, refer to
    the users and ingredients tables, respectively.
    """

    __tablename__ = "saved_ingredients"
    id = DATABASE.Column(
        DATABASE.Integer, unique=True, nullable=False, primary_key=True
    )
    user_id = DATABASE.Column(
        DATABASE.String(255),
        DATABASE.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id = DATABASE.Column(
        DATABASE.Integer,
        DATABASE.ForeignKey("ingredients.id", onupdate="CASCADE", ondelete="NO ACTION"),
        nullable=False,
    )
    ingredient = relationship(Ingredient, foreign_keys=[ingredient_id])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `ingredient_id` key
                will be replaced with an `ingredient` key
                which will map to the actual target object.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"user_id": self.user_id, "ingredient_id": self.ingredient_id}
        return {"user_id": self.user_id, "ingredient": self.ingredient.to_json()}


class Intolerance(DATABASE.Model):
    """
    The intolerances table is used to store information about a user's
    selected intolerances. Intolerance information is used to determine
    and restrict which recipes and ingredients a user sees.
    """

    __tablename__ = "intolerances"
    id = DATABASE.Column(
        DATABASE.Integer, unique=True, nullable=False, primary_key=True
    )
    user_id = DATABASE.Column(
        DATABASE.String(255),
        DATABASE.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    intolerance = DATABASE.Column(DATABASE.String(50), nullable=False)

    def to_json(self):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Returns:
            This row instance as a JSON object.
        """
        return {"user_id": self.user_id, "intolerance": self.intolerance}


class Relationship(DATABASE.Model):
    """
    The friends table is used to store relationship information between users.
    It does not store actual user data. To retrieve user information,
    refer to the users table.
    """

    __tablename__ = "friends"
    id = DATABASE.Column(
        DATABASE.Integer, unique=True, nullable=False, primary_key=True
    )
    user1 = DATABASE.Column(
        DATABASE.String(255),
        DATABASE.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    user2 = DATABASE.Column(
        DATABASE.String(255),
        DATABASE.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    user1_obj = relationship(User, foreign_keys=[user1])
    user2_obj = relationship(User, foreign_keys=[user2])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `user1` and `user2` keys
                will map to actual user objects instead of just their IDs.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"user1": self.user1, "user2": self.user2}

        return {"user1": self.user1_obj.to_json(), "user2": self.user2_obj.to_json()}


class Password(DATABASE.Model):
    """
    The passwords table stores passwords for all users with `DEFAULT`
    authentication. Passwords stored in this table are salted and encrypted.
    """

    __tablename__ = "passwords"
    id = DATABASE.Column(
        DATABASE.Integer, unique=True, nullable=False, primary_key=True
    )
    user_id = DATABASE.Column(
        DATABASE.String(255),
        DATABASE.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    phrase = DATABASE.Column(DATABASE.Text, nullable=False)
    user_obj = relationship(User, foreign_keys=[user_id])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `user_id` key
                will be replaced with a `user` key which will map
                to the actual user object instead of just the ID.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"user_id": self.user_id, "phrase": self.phrase}

        return {
            "user": self.user_obj.to_json(),
            "phrase": self.phrase,
        }


class FriendRequest(DATABASE.Model):
    """
    The friend_requests table is used to store friend requests.
    If the request is confirmed, a new entry in the friends table
    is created. Otherwise, the friend request is simply deleted.
    """

    __tablename__ = "friend_requests"
    id = DATABASE.Column(
        DATABASE.Integer, unique=True, nullable=False, primary_key=True
    )
    src = DATABASE.Column(
        DATABASE.String(255),
        DATABASE.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    target = DATABASE.Column(
        DATABASE.String(255),
        DATABASE.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    src_obj = relationship(User, foreign_keys=[src])
    target_obj = relationship(User, foreign_keys=[target])

    def to_json(self, shallow: bool = True):
        """
        Returns this row as a JSON object, where each key corresponds to a column
        in the table and the values correspond to the entries in the current row.

        Args:
            shallow (bool): If set to false, the `src` and `target` keys
                will map to actual user objects instead of just their IDs.

        Returns:
            This row instance as a JSON object.
        """
        if shallow:
            return {"src": self.src, "target": self.target}

        return {"src": self.src_obj.to_json(), "target": self.target_obj.to_json()}
