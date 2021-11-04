"""
==================== COMMON DATABASE DEFINITIONS ====================
This file defines common types and functions used across all database-related calls.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getenv
import sqlalchemy.orm as orm
import builtins


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
        except:
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

    def get_saved_recipes(self, user_id: str) -> list[int]:
        """
        Returns the list of saved recipes for the user with the specified ID.

        Args:
            user_id (str): The ID of the target user.

        Returns:
            A list of recipe IDs associated with the specified user.
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

        return [x.id for x in recipes]

    def get_saved_ingredients(self, user_id: str) -> list[int]:
        """
        Returns the list of saved ingredients for the user with the specified ID.

        Args:
            user_id (str): The ID of the target user.

        Returns:
            A list of ingredient IDs associated with the specified user.
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

        return [x.id for x in ingredients]

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

    def add_user(self, id: str, email: str, name: str = ""):
        """
        Creates a new user with the specified information and adds it to the database, then returns the created user.

        Args:
            id (str): The ID of the user. This value must be unique across all users.
            email (str): The user's email. This field is not checked for validity.
            name (str): The user's name. This value is optional.

        Returns:
            The newly created `User` object.

        Raises:
            DuplicateUserException: If a user with the specified ID already exists.
            DatabaseException: If there was a problem adding the user.
        """
        from database.models import User

        if self.user_exists(id):
            raise DuplicateUserException(id)

        user = User(id=id, email=email, name=name)

        session = self.int__Session()
        try:
            session.add(user)
            session.commit()
        except:
            session.rollback()
            raise DatabaseException("Failed to add user")
        finally:
            session.close()

        return user

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
