"""
==================== COMMON DATABASE DEFINITIONS ====================
This file defines common types and functions used across all database-related calls.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getenv
import sqlalchemy.orm as orm
from sqlalchemy import or_, and_
import builtins
from random import randrange


class DatabaseException(Exception):
    """
    Raised when there is a general problem during a database access.
    """

    def __init__(self, message=""):
        self.message = message


class NoUserException(DatabaseException):
    """
    Raised when the specified user does not exist in the database.
    """

    def __init__(self, user_id: str):
        super().__init__(f'No user with ID "{user_id}" exists in the database')


class NoRecipeException(DatabaseException):
    """
    Raised when the specified recipe does not exist in the database.
    """

    def __init__(self, recipe_id: int):
        super().__init__(f'No recipe with ID "{recipe_id}" exists in the database')


class NoIngredientException(DatabaseException):
    """
    Raised when the specified ingredient does not exist in the database.
    """

    def __init__(self, ingredient_id: int):
        super().__init__(
            f'No ingredient with ID "{ingredient_id}" exists in the database'
        )


class DuplicateUserException(DatabaseException):
    """
    Raised when the specified user already exists in the database.
    """

    def __init__(self, user_id: str):
        super().__init__(f'User with ID "{user_id}" already exists in the database')


class DuplicateRecipeException(DatabaseException):
    """
    Raised when the specified recipe already exists in the database.
    """

    def __init__(self, recipe_id: int):
        super().__init__(f'Recipe with ID "{recipe_id}" already exists in the database')


class DuplicateIngredientException(DatabaseException):
    """
    Raised when the specified ingredient already exists in the database.
    """

    def __init__(self, ingredient_id: int):
        super().__init__(
            f'Ingredient with ID "{ingredient_id}" already exists in the database'
        )


class InvalidIntoleranceException(DatabaseException):
    """
    Raised when the specified intolerance is invalid.
    """

    def __init__(self, intolerance: str):
        super().__init__(f'The specified intolerance "{intolerance}" does not exist')


class Database:
    def __init__(self, app: Flask):
        """
        Initializes the server's internal representation of the application database and allows it to connect to the database.
        This function must be called prior to calling any other function in this file.
        The `DATABASE_URL` environment variable must be defined before calling this function.

        Args:
            app (Flask): The Flask application object.

        Raises:
            DatabaseException: If the database URL could not be retrieved or if there was a problem initializing the database.
        """

        db_url = getenv("DATABASE_URL")

        if db_url == None:
            raise DatabaseException("Undefined database URL")
        elif db_url.startswith("postgres:"):
            # Sometimes, the database URL may start with "postgres:" instead of "postgresql:" (particularly Heroku).
            # This line corrects that issue.
            db_url = "postgresql" + db_url[8:]

        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        # Gets rid of a warning
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        self.int__db_obj = SQLAlchemy(app)
        self.int__Session = orm.sessionmaker(self.int__db_obj.engine)

        builtins.piecemeal_db_obj = self

    def get_db_obj(self) -> SQLAlchemy:
        """
        Returns the `SQLAlchemy` object associated with this database.
        """
        return self.int__db_obj

    def finalize(self):
        """
        Finalizes the database by closing all currently open sessions.
        This function must be called after all database-related tasks are complete and before the application shuts down.
        """
        self.int__db_obj.session.close_all()

    def get_user(self, id: str):
        """
        Returns the `User` object associated with the provided user ID.

        Args:
            id (str): The ID of the target user.

        Returns:
            The user object associated with the provided ID, or `None` if the specified user does not exist.

        Raises:
            DatabaseException: If there was a problem querying the user.
        """
        from database.models import User

        session = self.int__Session()
        user = None
        try:
            user = session.query(User).filter_by(id=id).first()
        except Exception as e:
            session.rollback()
            raise DatabaseException("Failed to perform query")
        finally:
            session.close()
        return user

    def user_exists(self, id: str) -> bool:
        """
        Returns true if the user with the specified ID exists.

        Args:
            id (str): The ID of the target user.

        Returns:
            True if the user with the specified ID exists.

        Raises:
            DatabaseException: If there was a problem querying the user.
        """
        return self.get_user(id) != None

    def get_recipe(self, id: int):
        """
        Returns the `Recipe` object associated with the provided ID.

        Args:
            id (int): The ID of the target recipe.

        Returns:
            The recipe object associated with the provided ID, or `None` if the specified recipe does not exist.

        Raises:
            DatabaseException: If there was a problem querying the recipe.
        """
        from database.models import Recipe

        session = self.int__Session()
        recipe = None
        try:
            recipe = session.query(Recipe).filter_by(id=id).first()
        except:
            session.rollback()
            raise DatabaseException("Failed to perform query")
        finally:
            session.close()
        return recipe

    def get_ingredient(self, id: int):
        """
        Returns the `Ingredient` object associated with the provided ID.

        Args:
            id (int): The ID of the target ingredient.

        Returns:
            The ingredient object associated with the provided ID, or `None` if the specified ingredient does not exist.

        Raises:
            DatabaseException: If there was a problem querying the ingredient.
        """
        from database.models import Ingredient

        session = self.int__Session()
        ingredient = None
        try:
            ingredient = session.query(Ingredient).filter_by(id=id).first()
        except:
            session.rollback()
            raise DatabaseException("Failed to perform query")
        finally:
            session.close()
        return ingredient

    def get_saved_recipes(self, user_id: str) -> list:
        """
        Returns the list of saved recipes for the user with the specified ID.

        Args:
            user_id (str): The ID of the target user.

        Returns:
            A list of recipe objects associated with the specified user.
            If the specified user has no saved recipes, this function will return an empty list.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If there was a problem querying the recipes.
        """
        from database.models import SavedRecipe

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        session = self.int__Session()
        recipes = []
        try:
            recipes = session.query(SavedRecipe).filter_by(user_id=user_id).all()
        except:
            session.rollback()
            raise DatabaseException("Failed to perform query")
        finally:
            session.close()

        return [x.recipe for x in recipes]

    def get_saved_ingredients(self, user_id: str) -> list[int]:
        """
        Returns the list of saved ingredients for the user with the specified ID.

        Args:
            user_id (str): The ID of the target user.

        Returns:
            A list of ingredient objects associated with the specified user.
            If the specified user has no saved ingredients, this function will return an empty list.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If there was a problem querying the ingredients.
        """
        from database.models import SavedIngredient

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        session = self.int__Session()
        ingredients = []
        try:
            ingredients = (
                session.query(SavedIngredient).filter_by(user_id=user_id).all()
            )
        except:
            session.rollback()
            raise DatabaseException("Failed to perform query")
        finally:
            session.close()

        return [x.ingredient for x in ingredients]

    def get_intolerances(self, user_id: str) -> list[str]:
        """
        Returns the list of intolerances for the user with the specified ID.

        Args:
            user_id (str): The ID of the target user.

        Returns:
            A list of intolerances associated with the specified user.
            If the specified user has no associated intolerances, this function will return an empty list.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If there was a problem querying the intolerances.
        """
        from database.models import Intolerance

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        session = self.int__Session()
        intolerances = []
        try:
            intolerances = session.query(Intolerance).filter_by(user_id=user_id).all()
        except:
            session.rollback()
            raise DatabaseException("Failed to perform query")
        finally:
            session.close()

        return [x.intolerance for x in intolerances]

    def username_exists(self, username: str) -> bool:
        """
        Returns true if any user in the database has the specified username.

        Args:
            username (str): The username to check.

        Returns:
            True if any user in the database has the specified username and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
        """
        from database.models import User

        session = self.int__Session()
        has_username = False
        try:
            has_username = (
                session.query(User).filter_by(username=username).first() is not None
            )
        except:
            session.rollback()
            raise DatabaseException("Failed to perform query")
        finally:
            session.close()

        return has_username

    def generate_username(self, given_name: str) -> str:
        """
        Generates a username based on the given name.

        The returned username is guaranteed to be unique across all users in the database.
        """
        # Get up to the first 10 valid characters in the given name. Convert any uppercase characters to lowercase ones.
        prefix = ""
        char_count = 0
        for char in given_name.lower():
            if not self.is_valid_username_char(char):
                continue
            prefix += char
            char_count += 1

            if char_count == 10:
                break

        prefix += "-"

        from random import randint

        # Randomly generate a 5-digit suffix.
        suffix_digits = 5
        suffix_number = randint(0, 10 ** suffix_digits - 1)
        format_string = f"%{suffix_digits}d"
        uname = prefix + str(format_string % suffix_number)
        tries = 1
        while self.username_exists(uname):
            # The algorithm will try up to suffix_digits number of times to generate a username.
            # If it still fails to generate a unique username after this point, the number of digits in the suffix will increase by 1 and the process will begin again.
            suffix_number = randint(0, 10 ** suffix_digits - 1)
            format_string = f"%{suffix_digits}d"
            uname = prefix + str(format_string % suffix_number)
            tries += 1

            if tries >= suffix_digits:
                tries = 0
                suffix_digits += 1

        return uname

    def is_valid_username_char(self, char: str) -> bool:
        return (
            char.isalnum() or char == "_" or char == "-" or char == "." or char == "$"
        )

    def username_is_valid(self, username: str) -> bool:
        """
        Returns true if the specified username does not contain any invalid characters.

        The list of valid characters includes:
        - Uppercase and lowercase Latin letters
        - Arabic numerals
        - Underscores, hyphens, periods, and dollar signs

        As a regular expression, a character is valid if it matches the following pattern:
        `[a-zA-Z0-9_-\.\$]`
        """
        for char in username:
            if not self.is_valid_username_char(char):
                return False
        return True

    def add_user(
        self,
        id: str,
        email: str,
        username: str = None,
        name: str = "",
        profile_image: str = "",
    ):
        """
        Creates a new user with the specified information and adds it to the database, then returns the created user.

        Args:
            id (str): The ID of the user. This value must be unique across all users.
            email (str): The user's email. This field is not checked for validity.
            username (str): The user's username. This value must be unique across all users and must be at least three characters.
                If the username is not provided, then a new one will be randomly generated based on the user's given name.
            name (str): The user's name. This value is optional.
            profile_image (str): The URL for the user's profile picture. This value is optional.

        Returns:
            The newly created `User` object.

        Raises:
            DuplicateUserException: If a user with the specified ID (or username) already exists.
            DatabaseException: If there was a problem adding the user.
        """
        from database.models import User

        if self.user_exists(id):
            raise DuplicateUserException(id)
        if username != None and self.username_exists(username):
            raise DuplicateUserException(username)

        # If the username is None, generate a new one
        if username == None:
            username = self.generate_username(name)

        # If the username is too short, raise an exception
        if len(username) < 3:
            raise DatabaseException(f'The specified username "{username}" is too short')

        # If the username contains invalid characters, raise an exception
        if not self.username_is_valid(username):
            raise DatabaseException(
                f'The specified username "{username}" contains invalid characters'
            )

        user = User(
            id=id,
            email=email,
            name=name,
            profile_image=profile_image,
            username=username,
        )

        session = self.int__Session()
        try:
            session.add(user)
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to add user")
        finally:
            session.close()

        return self.get_user(id)

    def add_recipe(self, id: int, name: str, image: str):
        """
        Creates a new recipe with the specified information and adds it to the database, then returns the created recipe.

        Args:
            id (int): The ID of the recipe. This value must be unique across all recipes.
            name (str): The name of the recipe.
            image (str): The URL for the recipe image.

        Returns:
            The newly created `Recipe` object.

        Raises:
            DuplicateRecipeException: If a recipe with the specified ID already exists.
            DatabaseException: If there was a problem adding the recipe.
        """
        from database.models import Recipe

        if self.get_recipe(id) != None:
            raise DuplicateRecipeException(id)

        recipe = Recipe(id=id, name=name, image=image)

        session = self.int__Session()
        try:
            session.add(recipe)
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to add recipe")
        finally:
            session.close()

        return recipe

    def add_ingredient(self, id: int, name: str, image: str):
        """
        Creates a new ingredient with the specified information and adds it to the database, then returns the created ingredient.

        Args:
            id (int): The ID of the ingredient. This value must be unique across all ingredients.
            name (str): The name of the ingredient.
            image (str): The URL for the ingredient image.

        Returns:
            The newly created `Ingredient` object.

        Raises:
            DuplicateIngredientException: If a ingredient with the specified ID already exists.
            DatabaseException: If there was a problem adding the ingredient.
        """
        from database.models import Ingredient

        if self.get_ingredient(id) != None:
            raise DuplicateIngredientException(id)

        ingredient = Ingredient(id=id, name=name, image=image)

        session = self.int__Session()
        try:
            session.add(ingredient)
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to add ingredient")
        finally:
            session.close()

        return ingredient

    def add_saved_recipe(self, user_id: str, recipe_id: int):
        """
        Adds the recipe with the specified ID to the specified user's list of saved recipes.

        Args:
            user_id (str): The ID of the user.
            recipe_id (int): The ID of the recipe.

        Raises:
            NoUserException: If the specified user does not exist.
            NoRecipeException: If the specified recipe does not exist.
            DatabaseException: If there was a problem adding the recipe.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        if self.get_recipe(recipe_id) == None:
            raise NoRecipeException(recipe_id)

        from database.models import SavedRecipe

        recipe = SavedRecipe(user_id=user_id, recipe_id=recipe_id)

        session = self.int__Session()
        try:
            session.add(recipe)
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to add recipe")
        finally:
            session.close()

    def add_saved_ingredient(self, user_id: str, ingredient_id: int):
        """
        Adds the ingredient with the specified ID to the specified user's list of saved ingredients.

        Args:
            user_id (str): The ID of the user.
            ingredient_id (int): The ID of the ingredient.

        Raises:
            NoUserException: If the specified user does not exist.
            NoRecipeException: If the specified ingredient does not exist.
            DatabaseException: If there was a problem adding the ingredient.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        if self.get_ingredient(ingredient_id) == None:
            raise NoIngredientException(ingredient_id)

        from database.models import SavedIngredient

        ingredient = SavedIngredient(user_id=user_id, ingredient_id=ingredient_id)

        session = self.int__Session()
        try:
            session.add(ingredient)
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to add ingredient")
        finally:
            session.close()

    def add_intolerance(self, user_id: str, intolerance: str):
        """
        Adds the tolerance with the specified name to the specified user's list of saved intolerances.

        Args:
            user_id (str): The ID of the user.
            intolerance (str): The intolerance to add.

        Raises:
            NoUserException: If the specified user does not exist.
            InvalidIntoleranceException: If the intolerance is invalid.
            DatabaseException: If there was a problem adding the intolerance.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        import api.spoonacular as spoonacular

        if not spoonacular.Intolerance.has(intolerance):
            raise InvalidIntoleranceException(intolerance)

        from database.models import Intolerance

        session = self.int__Session()
        try:
            session.add(Intolerance(user_id=user_id, intolerance=intolerance))
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to add intolerance")
        finally:
            session.close()

    def delete_user(self, id: str):
        """
        Deletes the user with the specified ID, including all associated rows in any linked tables (cascade delete).

        Args:
            id (str): The ID of the user to delete.

        Raises:
            NoUserException: If the user does not exist.
            DatabaseException: If there was a problem deleting the user.
        """

        if not self.user_exists(id):
            raise NoUserException(id)

        from database.models import User

        session = self.int__Session()
        try:
            session.query(User).filter_by(id=id).delete()
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to delete user")
        finally:
            session.close()

    def delete_recipe(self, id: int):
        """
        Deletes the recipe with the specified ID, including all associated rows in any linked tables (cascade delete).
        It's not recommended to call this function unless no users have this recipe saved, otherwise it may cause problems for those that still do!

        Args:
            id (int): The ID of the recipe to delete.

        Raises:
            NoRecipeException: If the recipe does not exist.
            DatabaseException: If there was a problem deleting the recipe.
        """

        if self.get_recipe(id) == None:
            raise NoRecipeException(id)

        from database.models import Recipe

        session = self.int__Session()
        try:
            session.query(Recipe).filter_by(id=id).delete()
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to delete recipe")
        finally:
            session.close()

    def delete_ingredient(self, id: int):
        """
        Deletes the ingredient with the specified ID, including all associated rows in any linked tables (cascade delete).
        It's not recommended to call this function unless no users have this ingredient saved, otherwise it may cause problems for those that still do!

        Args:
            id (int): The ID of the ingredient to delete.

        Raises:
            NoIngredientException: If the ingredient does not exist.
            DatabaseException: If there was a problem deleting the ingredient.
        """

        if self.get_ingredient(id) == None:
            raise NoIngredientException(id)

        from database.models import Ingredient

        session = self.int__Session()
        try:
            session.query(Ingredient).filter_by(id=id).delete()
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to delete ingredient")
        finally:
            session.close()

    def delete_saved_recipe(self, user_id: str, recipe_id: int):
        """
        Deletes the recipe saved by the specified user.
        If the user does not have the recipe saved, this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            recipe_id (int): The ID of the target recipe.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If there was a problem deleting the recipe.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        from database.models import SavedRecipe

        session = self.int__Session()
        try:
            session.query(SavedRecipe).filter_by(
                user_id=user_id, recipe_id=recipe_id
            ).delete()
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to delete recipe")
        finally:
            session.close()

    def delete_saved_ingredient(self, user_id: str, ingredient_id: int):
        """
        Deletes the ingredient saved by the specified user.
        If the user does not have the ingredient saved, this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            ingredient_id (int): The ID of the target ingredient.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If there was a problem deleting the ingredient.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        from database.models import SavedIngredient

        session = self.int__Session()
        try:
            session.query(SavedIngredient).filter_by(
                user_id=user_id, ingredient_id=ingredient_id
            ).delete()
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to delete ingredient")
        finally:
            session.close()

    def delete_intolerance(self, user_id: str, intolerance: str):
        """
        Deletes the intolerance associated with the specified user.
        If the user does not have the associated intolerance, this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            intolerance (str): The ID of the target intolerance.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If there was a problem deleting the intolerance.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        from database.models import Intolerance

        session = self.int__Session()
        try:
            session.query(Intolerance).filter_by(
                user_id=user_id, intolerance=intolerance
            ).delete()
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to delete intolerance")
        finally:
            session.close()

    def add_relationship(self, user1: str, user2: str) -> bool:
        """
        Adds a two-way relationship between the specified users.

        If the relationship already exists, this function does nothing.

        A relationship does not consider the position of the users to be significant when determining if a relationship exists.
        This means that for users A and B, calling `add_relationship(A, B)`
        is the same as calling `add_relationship(B, A)`.

        Args:
            user1 (str): The ID of the first user in the relationship.
            user2 (str): The ID of the second user in the relationship.

        Returns:
            True if the relationship was added successfully and false if the relationship already exists.

        Raises:
            NoUserException: If either of the specified users do not exist.
            DatabaseException: If there was a problem adding the relationship.
        """

        if not self.user_exists(user1):
            raise NoUserException(user1)
        if not self.user_exists(user2):
            raise NoUserException(user2)

        from database.models import Relationship

        session = self.int__Session()
        try:
            # I didn't use has_relationship() here because it performs too many checks and setups that have already been performed.
            has_relationship = (
                session.query(Relationship)
                .filter(
                    or_(and_(user1=user1, user2=user2), and_(user1=user2, user2=user1))
                )
                .first()
                is not None
            )
            if has_relationship:
                return False

            session.add(Relationship(user1=user1, user2=user2))
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to add relationship")
        finally:
            session.close()

        return True

    def has_relationship(self, user1: str, user2: str) -> bool:
        """
        Returns true if a relationship between the specified users exists.

        A relationship does not consider the position of the users to be significant when determining if a relationship exists.
        This means that for users A and B, calling `has_relationship(A, B)`
        is the same as calling `has_relationship(B, A)`.

        Args:
            user1 (str): The ID of the first user in the relationship.
            user2 (str): The ID of the second user in the relationship.

        Returns:
            True if a relationship exists between the specified users and false otherwise.

        Raises:
            NoUserException: If either of the specified users do not exist.
            DatabaseException: If there was a problem querying the relationship.
        """
        if not self.user_exists(user1):
            raise NoUserException(user1)
        if not self.user_exists(user2):
            raise NoUserException(user2)

        from database.models import Relationship

        session = self.int__Session()
        has_relationship = False
        try:
            has_relationship = (
                session.query(Relationship)
                .filter(
                    or_(and_(user1=user1, user2=user2), and_(user1=user2, user2=user1))
                )
                .first()
                is not None
            )
        except:
            session.rollback()
            raise DatabaseException("Failed to query relationship")
        finally:
            session.close()

        return has_relationship

    def delete_relationship(self, user1: str, user2: str) -> bool:
        """
        Deletes the relationship between the specified users.

        If the relationship does not exist, this function does nothing.

        Args:
            user1 (str): The ID of the first user in the relationship.
            user2 (str): The ID of the second user in the relationship.

        Returns:
            True if the relationship was deleted successfully and false otherwise.

        Raises:
            NoUserException: If either of the specified users do not exist.
            DatabaseException: If there was a problem deleting the relationship.
        """
        if not self.user_exists(user1):
            raise NoUserException(user1)
        if not self.user_exists(user2):
            raise NoUserException(user2)

        from database.models import Relationship

        session = self.int__Session()
        try:
            # I didn't use has_relationship() here because it performs too many checks and setups that have already been performed.
            relationship = (
                session.query(Relationship)
                .filter(
                    or_(and_(user1=user1, user2=user2), and_(user1=user2, user2=user1))
                )
                .first()
            )
            if relationship == None:
                return False

            session.delete(relationship)
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to delete relationship")
        finally:
            session.close()

        return True

    def get_relationships_for_user(self, user: str):
        """
        Returns a list of user objects which have relationships with the specified user.

        Args:
            user (str): The ID of the target user.

        Returns:
            A list of user objects which have relationships with the specified user.
            If the user has no relationships, this function will return an empty list.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If there was a problem querying the relationships.
        """

        if not self.user_exists(user):
            raise NoUserException(user)

        from database.models import Relationship

        session = self.int__Session()
        users = []
        try:
            user1_relationships = (
                session.query(Relationship).filter_by(user1=user).all()
            )
            for relationship in user1_relationships:
                users.append(relationship.user2_obj)
            user2_relationships = (
                session.query(Relationship).filter_by(user2=user).all()
            )
            for relationship in user2_relationships:
                users.append(relationship.user1_obj)
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to query relationships")
        finally:
            session.close()

        return users

    def get_recommended_recipes_from_user(self, user: str, limit: int = 5):
        """
        Returns a list of recipe objects based on the specified user's saved recipes.

        The algorithm will look at only the most recently liked recipes and will only retrieve up to
        the specified limit of recipes.

        Args:
            user (str): The ID of the target user.
            limit (int): The limit of the number of recipes to retrieve.

        Returns:
            A list of recipe objects, or an empty list if the user has no saved recipes.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If the recipes could not be retrieved.
        """
        recipes = self.get_saved_recipes(user)

        result = {}

        recipes_len = len(recipes)

        recipe_count = min(limit, recipes_len)

        # The max number of tries the algorithm will do to find a new recipe before it gives up on the current iteration
        MAX_TRIES = 10

        for _ in range(0, recipe_count):
            # The algorithm starts trying to sample from the first recipe_count number of recipes and incrementally increases its search range until it equals the length of the original list.
            current_range = recipe_count
            index = randrange(
                recipes_len - current_range, recipes_len
            )  # We sample from the end of the list because that's where the most recent recipes are
            tries = 0
            while recipes[index].id in result and tries <= MAX_TRIES:
                # Increase the search range if it's still less than the length of the actual list
                if current_range < recipes_len:
                    current_range += 1
                index = randrange(recipes_len - current_range, recipes_len)
                tries += 1
            if recipes[index].id in result:
                continue
            result[recipes[index].id] = recipes[index]

        return list(result.values())

    def get_recommended_recipes_from_relationships(
        self, user: str, limit_friends: int = 5, limit_per_relationship: int = 5
    ):
        """
        Returns a JSON object containing lists of recipes generated based off of the liked recipes of the specified user's friends.

        The algorithm will look at only the most recently liked recipes and will only retrieve up to
        the specified limit of recipes per friend.

        Args:
            user (str): The ID of the target user.
            limit_friends (int): The limit of the number of friends to sample.
            limit_per_relationship (int): The limit of the number of recipes to retrieve per friend.

        Returns:
            A JSON object containing lists of recommended recipes, whose format is the following:
            {
                "id1": {
                    "userdata": <user_obj>,
                    "recipes": [<recipe_obj>]
                },
                "id2": {
                    "userdata": <user_obj>,
                    "recipes": [<recipe_obj>]
                },
                ...
            }

            The returned object is a dictionary of user IDs to values containing two fields.

            `userdata` maps to the JSON representation of the associated user object.
            `recipes` maps to a list containing JSON representations of the selected recipe objects.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If the recipes could not be retrieved.
        """
        if not self.user_exists(user):
            raise NoUserException(user)

        friends = self.get_relationships_for_user(user)

        result = {}

        friend_count = min(len(friends), limit_friends)

        # The max number of tries the algorithm will do to find a new friend before it gives up on the current iteration
        MAX_TRIES = 10

        for _ in range(0, friend_count):
            index = randrange(len(friends))
            tries = 0
            while friends[index].id in result and tries <= MAX_TRIES:
                index = randrange(len(friends))
                tries += 1
            if friends[index].id in result:
                continue
            recipes = self.get_recommended_recipes_from_user(
                friends[index], limit_per_relationship
            )
            result[friends[index].id] = {"userdata": friends[index], "recipes": recipes}

        return result

    def get_recommended_ingredients_from_user(self, user: str, limit: int = 5):
        """
        Returns a list of ingredient objects based on the specified user's saved ingredients.

        The algorithm will look at only the most recently liked ingredients and will only retrieve up to
        the specified limit of ingredients.

        Args:
            user (str): The ID of the target user.
            limit (int): The limit of the number of ingredients to retrieve.

        Returns:
            A list of ingredient objects, or an empty list if the user has no saved ingredients.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If the ingredients could not be retrieved.
        """
        ingredients = self.get_saved_ingredients(user)

        result = {}

        ingredients_len = len(ingredients)

        ingredient_count = min(limit, ingredients_len)

        # The max number of tries the algorithm will do to find a new ingredient before it gives up on the current iteration
        MAX_TRIES = 10

        for _ in range(0, ingredient_count):
            # The algorithm starts trying to sample from the first ingredient_count number of ingredients and incrementally increases its search range until it equals the length of the original list.
            current_range = ingredient_count
            index = randrange(
                ingredients_len - current_range, ingredients_len
            )  # We sample from the end of the list because that's where the most recent ingredients are
            tries = 0
            while ingredients[index].id in result and tries <= MAX_TRIES:
                # Increase the search range if it's still less than the length of the actual list
                if current_range < ingredients_len:
                    current_range += 1
                index = randrange(ingredients_len - current_range, ingredients_len)
                tries += 1
            if ingredients[index].id in result:
                continue
            result[ingredients[index].id] = ingredients[index]

        return list(result.values())

    def get_recommended_ingredients_from_relationships(
        self, user: str, limit_friends: int = 5, limit_per_relationship: int = 5
    ):
        """
        Returns a JSON object containing lists of ingredients generated based off of the liked ingredients of the specified user's friends.

        The algorithm will look at only the most recently liked ingredients and will only retrieve up to
        the specified limit of ingredients per friend.

        Args:
            user (str): The ID of the target user.
            limit_friends (int): The limit of the number of friends to sample.
            limit_per_relationship (int): The limit of the number of ingredients to retrieve per friend.

        Returns:
            A JSON object containing lists of recommended ingredients, whose format is the following:
            {
                "id1": {
                    "userdata": <user_obj>,
                    "ingredients": [<ingredient_obj>]
                },
                "id2": {
                    "userdata": <user_obj>,
                    "ingredients": [<ingredient_obj>]
                },
                ...
            }

            The returned object is a dictionary of user IDs to values containing two fields.

            `userdata` maps to the JSON representation of the associated user object.
            `ingredients` maps to a list containing JSON representations of the selected ingredient objects.

        Raises:
            NoUserException: If the specified user does not exist.
            DatabaseException: If the ingredients could not be retrieved.
        """
        if not self.user_exists(user):
            raise NoUserException(user)

        friends = self.get_relationships_for_user(user)

        result = {}

        friend_count = min(len(friends), limit_friends)

        # The max number of tries the algorithm will do to find a new friend before it gives up on the current iteration
        MAX_TRIES = 10

        for _ in range(0, friend_count):
            index = randrange(len(friends))
            tries = 0
            while friends[index].id in result and tries <= MAX_TRIES:
                index = randrange(len(friends))
                tries += 1
            if friends[index].id in result:
                continue
            ingredients = self.get_recommended_ingredients_from_user(
                friends[index], limit_per_relationship
            )
            result[friends[index].id] = {
                "userdata": friends[index],
                "ingredients": ingredients,
            }

        return result

    def set_username(self, user_id: str, new_username: str):
        """
        Sets the username for the user with the specified ID.

        Usernames must be unique across all users, must be at least three characters long, and can only contain the following characters:
        - Uppercase and lowercase Latin letters
        - Arabic numerals
        - Underscores, hyphens, periods, and dollar signs

        Args:
            user_id (str): The ID of the target user.
            new_username (str): The new username the user should have.

        Raises:
            NoUserException: If the user with the specified ID does not exist.
            DuplicateUserException: If a user with the specified username already exists.
            DatabaseException: If the username could not be set.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)
        if self.username_exists(new_username):
            raise DuplicateUserException(new_username)
        if not self.username_is_valid(new_username):
            raise DatabaseException(
                f'The specified username "{new_username}" contains invalid characters'
            )
        if len(new_username) < 3:
            raise DatabaseException(
                f'The specified username "{new_username}" is too short'
            )

        from database.models import User

        session = self.int__Session()
        try:
            session.query(User).filter_by(id=user_id).update({"username": new_username})
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to set username")
        finally:
            session.close()

    def search_users_by_given_name(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> list:
        """
        Searches for users whose given names match or otherwise contain the given query string and returns a list of user objects.

        Args:
            query (str): The query string to use.
            limit (int): The maximum number of users to return. This value is optional.
            offset (int): The offset into the total list of users to start at. This value is optional.

        Returns:
            A list of `User` objects whose given names match the provided search criteria, or an empty list if no users match the given criteria.

        Raises:
            DatabaseException: If the query was unable to be performed.
        """

        from database.models import User

        session = self.int__Session()
        result = []
        try:
            users = (
                session.query(User)
                .filter(User.name.ilike(f"%{query}%"))
                .offset(offset)
                .limit(limit)
                .all()
            )

            if users != None:
                result = users
        except:
            session.rollback()
            raise DatabaseException("Failed to query users")
        finally:
            session.close()

        return result

    def search_users_by_username(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> list:
        """
        Searches for users whose usernames match or otherwise contain the given query string and returns a list of user objects.

        Args:
            query (str): The query string to use.
            limit (int): The maximum number of users to return. This value is optional.
            offset (int): The offset into the total list of users to start at. This value is optional.

        Returns:
            A list of `User` objects whose usernames match the provided search criteria, or an empty list if no users match the given criteria.

        Raises:
            DatabaseException: If the query was unable to be performed.
        """

        from database.models import User

        session = self.int__Session()
        result = []
        try:
            users = (
                session.query(User)
                .filter(User.username.ilike(f"%{query}%"))
                .offset(offset)
                .limit(limit)
                .all()
            )

            if users != None:
                result = users
        except:
            session.rollback()
            raise DatabaseException("Failed to query users")
        finally:
            session.close()

        return result
