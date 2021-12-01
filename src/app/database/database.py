# pylint: disable=too-many-lines
# All of the database functions need to go in here
"""
==================== COMMON DATABASE DEFINITIONS ====================
This file defines common types and functions used across all database-related calls.
"""

import builtins
from enum import Enum
from os import getenv
from random import randbytes, randint, randrange
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm
from sqlalchemy.sql.expression import and_, or_, func
from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHash,
    VerificationError,
    HashingError,
    VerifyMismatchError,
)
from ..util import (
    dict_list_contains,
    get_or_raise,
    get_or_default,
    get_or_default_func,
)


class ProfileVisibility(Enum):
    """
    This type specifies all of the possible values for the
    `profile_visibility` field in the `users` table.
    """

    NAME = 0x01
    CREATION_DATE = 0x02
    INTOLERANCES = 0x04
    SAVED_RECIPES = 0x08
    SAVED_INGREDIENTS = 0x10
    FRIENDS = 0x20

    def __init__(self, value):
        self._value_ = value

    @classmethod
    def has(cls, bitfield: int, value) -> bool:
        """
        Returns true if `bitfield` has the specified ProfileVisibility `value`.
        """
        return (bitfield & value.value) == value.value

    @classmethod
    def enable(cls, bitfield: int, value) -> int:
        """
        Enables the specified ProfileVisibility `value` in `bitfield`.
        """
        return bitfield | value

    @classmethod
    def disable(cls, bitfield: int, value) -> int:
        """
        Disables the specified ProfileVisibility `value` in `bitfield`.
        """
        return bitfield & ~value

    @classmethod
    def enable_all(cls) -> int:
        """
        Returns a bitfield which has all ProfileVisibility values enabled.
        """
        return 0xFF

    @classmethod
    def disable_all(cls) -> int:
        """
        Returns a bitfield which has all ProfileVisibility values disabled.
        """
        return 0

    @classmethod
    def to_json(cls, bitfield: int) -> dict:
        """
        Creates a JSON object representing all of the permissions stored in `bitfield`.

        Each permission will be a mapping of the permission name (in lower snake case)
        to a boolean.
        """

        result = {}
        for field in ProfileVisibility:
            result[field.name.lower()] = ProfileVisibility.has(bitfield, field)
        return result


class UserIntolerance(Enum):
    """
    This type specifies the available intolerance types a user can have.
    """

    DAIRY = (0, "Dairy")
    EGG = (1, "Egg")
    GLUTEN = (2, "Gluten")
    GRAIN = (3, "Grain")
    PEANUT = (4, "Peanut")
    SEAFOOD = (5, "Seafood")
    SESAME = (6, "Sesame")
    SHELLFISH = (7, "Shellfish")
    SOY = (8, "Soy")
    SULFITE = (9, "Sulfite")
    TREE_NUT = (10, "Tree Nut")
    WHEAT = (11, "Wheat")

    def __init__(self, value, display_name):
        self._value_ = value
        self.display_name = display_name

    def get_display_name(self) -> str:
        """
        Returns the display name for this intolerance instance.
        """
        return self.display_name

    def to_json(self):
        """
        Returns a JSON representation of this intolerance instance.
        """
        return {"id": self.value, "name": self.display_name}

    @classmethod
    def get_from_id(cls, intolerance_id: int):
        """
        Returns the UserIntolerance object which corresponds to the specified ID,
        or None if no intolerance matches.
        """
        for intolerance in UserIntolerance:
            if intolerance.value == int(intolerance_id):
                return intolerance
        return None


class UserAuthentication(Enum):
    """
    This type specifies all of the possible methods a user can use to authorize themselves.
    """

    DEFAULT = (0,)
    GOOGLE = (1,)

    def get_id(self):
        """
        Returns the ID for the current element.
        """
        return self.value[0]

    @classmethod
    def get_from_value(cls, value: int):
        """
        Returns the enum instance associated with the provided value.
        """
        for member in cls:
            if value == member.get_id():
                return member
        raise ValueError()


class UserStatus(Enum):
    """
    This type specifies all of the possible statuses a user can have.
    """

    UNVERIFIED = (0,)
    VERIFIED = (1,)
    DEACTIVATED = (2,)

    def get_id(self):
        """
        Returns the ID for the current element.
        """
        return self.value[0]


class DatabaseException(Exception):
    """
    Raised when there is a general problem during a database access.
    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message


class NoUserException(DatabaseException):
    """
    Raised when the specified ID or username does not correspond to any user in the database.
    """

    def __init__(self, user_id: str, id_type="ID"):
        super().__init__(f"No user exists with {id_type} {user_id}")


class NoRecipeException(DatabaseException):
    """
    Raised when the specified ID does not correspond to any recipe in the database.
    """

    def __init__(self, recipe_id: int):
        super().__init__(f"No recipe exists with ID {recipe_id}")


class NoIngredientException(DatabaseException):
    """
    Raised when the specified ID does not correspond to any ingredient in the database.
    """

    def __init__(self, ingredient_id: int):
        super().__init__(f"No ingredient exists with ID {ingredient_id}")


class DuplicateUserException(DatabaseException):
    """
    Raised when the specified ID, username, or email already corresponds to a user in the database.
    """

    def __init__(self, problem_value: str, problem_type="ID"):
        super().__init__(f"A user already exists with {problem_type} {problem_value}")


class DuplicateRecipeException(DatabaseException):
    """
    Raised when the specified ID already corresponds to a recipe in the database.
    """

    def __init__(self, recipe_id: int):
        super().__init__(f"A recipe already exists with ID {recipe_id}")


class DuplicateIngredientException(DatabaseException):
    """
    Raised when the specified ID already corresponds to an ingredient in the database.
    """

    def __init__(self, ingredient_id: int):
        super().__init__(f"An ingredient already exists with ID {ingredient_id}")


class InvalidArgumentException(DatabaseException):
    """
    Raised when an argument to a database-related function is invalid.
    """

    def __init__(self, arg: str = None):
        if arg is None:
            super().__init__("Invalid arguments passed to function")
        else:
            super().__init__(f"Invalid argument passed to function: {arg}")


class EncryptionException(DatabaseException):
    """
    Raised when there is a problem ensuring the integrity of
    an encrypted piece of data in a database call.
    """

    def __init__(self, message=None):
        super().__init__(
            "Failed to maintain data integrity during encryption handling"
            if message is None
            else message
        )


# pylint: disable=too-many-public-methods
# All database-related methods must be contained in this class.
class Database:
    """
    Contains all database-related calls.
    Anything to do with the database must be accessed through an instance of this class.
    To access it, use the one defined in the `app` module.
    """

    def __init__(self, app: Flask):
        """
        Initializes the server's internal representation of the application database
        and allows it to connect to the database.
        This function must be called prior to calling any other function in this file.
        The `DATABASE_URL` environment variable must be defined before calling this function.

        Args:
            app (Flask): The Flask application object.

        Raises:
            DatabaseException: If the database URL could not be retrieved
                or if there was a problem initializing the database.
        """

        db_url = getenv("DATABASE_URL")

        if db_url is None:
            raise DatabaseException("Undefined database URL")

        if db_url.startswith("postgres:"):
            # Sometimes, the database URL may start with "postgres:"
            # instead of "postgresql:" (particularly with Heroku).
            # This line corrects that issue.
            db_url = "postgresql" + db_url[8:]

        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
        # Gets rid of a warning
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        self.db_obj = SQLAlchemy(app)
        self.session_generator = orm.sessionmaker(self.db_obj.engine)

        builtins.piecemeal_db_obj = self

    def get_db_obj(self) -> SQLAlchemy:
        """
        Returns the `SQLAlchemy` object associated with this database.
        """
        return self.db_obj

    # ===== INTERNAL UTILITY FUNCTIONS ===== #
    # These functions are not meant for use outside of this class!

    def generate_user_id(self):
        """
        Generates a user ID guaranteed to be unique against all current database users.

        This function will try up to 100 times to generate an ID.
        If it fails after 100 tries, it will raise a `DatabaseException`.
        """
        result = randbytes(255).hex()[0:255]
        tries = 0
        while self.user_exists(result) and tries < 100:
            result = randbytes(255).hex()[0:255]
            tries += 1
            if tries >= 100:
                raise DatabaseException("Failed to generate user ID")

        return result

    def username_exists(self, username: str) -> bool:
        """
        Returns true if any user exists in the database with the specified username.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                return (
                    session.query(User).filter_by(username=username).first() is not None
                )
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def generate_username(self):
        """
        Generates a username guaranteed to be unique against all current database users.

        This function will try up to 100 times to generate a username.
        If it fails after 100 tries, it will raise a `DatabaseException`.
        """
        prefix = "user-"

        digits = 5
        while digits < 11:
            suffix = randint(0, (10 ** digits) - 1)
            username = prefix + f"{suffix:0{digits}d}"
            tries = 0
            while tries < 10 and self.username_exists(username):
                suffix = randint(0, (10 ** digits) - 1)
                username = prefix + f"{suffix:0{digits}d}"
                tries += 1
            if not self.username_exists(username):
                return username
            digits += 1
        raise DatabaseException("Failed to generate username")

    def email_exists(self, email: str) -> bool:
        """
        Returns true if any user in the database has the specified email.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                return session.query(User).filter_by(email=email).first() is not None
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    @classmethod
    def validate_email(cls, email: str):
        """
        Checks the provided email for syntactic correctness
        and raises an `InvalidArgumentException` if the email is invalid.
        """
        if (
            re.fullmatch(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email)
            is None
        ):
            raise InvalidArgumentException("email has invalid syntax")

    @classmethod
    def validate_username(cls, username: str):
        """
        Checks the provided username for syntactic correctness
        and raises an `InvalidArgumentException` if the username is invalid.
        """
        if len(username) < 3:
            raise InvalidArgumentException("username is too short")
        if len(username) > 50:
            raise InvalidArgumentException("username is too long")
        if re.fullmatch(r"\b[a-zA-Z0-9_\-.$]+\b", username) is None:
            raise InvalidArgumentException("username has invalid syntax")

    @classmethod
    def validate_user_id(cls, user_id: str):
        """
        Checks the provided user ID for syntactic correctness
        and raises an `InvalidArgumentException` if the user ID is invalid.
        """
        if len(user_id) > 255:
            raise InvalidArgumentException("user ID is too long")
        if re.fullmatch(r"\b[\u0020-\u007E]+\b", user_id) is None:
            raise InvalidArgumentException("user ID has invalid syntax")

    @classmethod
    def generate_encrypted_password(cls, password: str) -> str:
        """
        Generates an encrypted version of the provided unencrypted password.

        Raises:
            EncryptionException: If the function failed to encrypt the password.
        """
        hasher = PasswordHasher()
        try:
            return hasher.hash(password)
        except Exception as exc:
            raise EncryptionException("Failed to encrypt password") from exc

    def get_user_password(self, user_id: str):
        """
        Returns the encrypted password associated with the provided user.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Password

        try:
            with self.session_generator(expire_on_commit=False) as session:
                password = session.query(Password).filter_by(user_id=user_id).first()
                if password is None:
                    raise NoUserException(user_id)
                return password.phrase
        except NoUserException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    # ===== USER MANAGEMENT ===== #

    def add_user(self, userdata: dict):
        """
        Creates a new user with the specified user data.

        Args:
            userdata (dict): A dictionary of user data values
                consisting of the following entries (required entries are listed first):
                authentication (int): The authentication type for the user.
                    This value must be one of the values specified
                    by the `UserAuthentication` type.
                    This value is required.
                email (str): The user's email.
                    This value must be unique across all users
                    and is checked for syntax correctness.
                    This value is required.
                password (str): The user's (unencrypted) password.
                    This value is only required for accounts
                    whose authentication method is `DEFAULT`.
                id (str): The internal ID of the user.
                    This value must be unique across all users.
                    If it is not present, this function will automatically generate a value.
                username (str): The username of the user.
                    This value must be unique across all users.
                    If it is not present, this function will automatically generate a value.
                given_name (str): The user's given name.
                    This value is optional.
                family_name (str): The user's family name.
                    This value is optional.
                profile_image (str): The URL for the user's profile image.
                    If it is not present, this function will automatically insert a default URL.
                status (int): The user's status.
                    This must be one of the values specified by the UserStatus type.
                    If it is not present, this function will automatically assign
                    a status of `UNVERIFIED` (due to the email having not yet been verified).
                profile_visibility (int): The user's profile visibility.
                    This must be a bitfield containing the values specified by
                    the ProfileVisibility type. If it is not present, this function will
                    automatically assign a value of 0 (all fields disabled).

        Raises:
            DatabaseException: If the function failed to create the user.
            DuplicateUserException: If a user already exists
                in the database with the specified ID, username, or email.
            InvalidArgumentException: If any of the provided arguments were invalid.
            EncryptionException: If the authentication method is `DEFAULT`
            and the provided password was unable to be properly encrypted.
        """

        auth: UserAuthentication = UserAuthentication.get_from_value(
            get_or_raise(
                userdata,
                "authentication",
                InvalidArgumentException("expected authentication"),
            )
        )

        email: str = get_or_raise(
            userdata, "email", InvalidArgumentException("expected email")
        )

        user_id: str = get_or_default_func(
            # pylint: disable=unnecessary-lambda
            # This lambda is necessary; we do not want the function to run
            # unless the key is not present
            userdata,
            "id",
            lambda: self.generate_user_id(),
        )

        username: str = get_or_default_func(
            # pylint: disable=unnecessary-lambda
            # This lambda is necessary; we do not want the function to run
            # unless the key is not present
            userdata,
            "username",
            lambda: self.generate_username(),
        )

        if self.email_exists(email):
            raise DuplicateUserException(email, "email")
        if self.username_exists(username):
            raise DuplicateUserException(username, "username")
        if self.user_exists(user_id):
            raise DuplicateUserException(user_id)

        Database.validate_email(email)
        Database.validate_username(username)
        Database.validate_user_id(user_id)

        given_name = get_or_default(userdata, "given_name", "")

        family_name = get_or_default(userdata, "family_name", "")

        profile_image = get_or_default(
            userdata, "profile_image", "/static/assets/default_user_profile_image.png"
        )

        status: UserStatus = get_or_default(userdata, "status", UserStatus.UNVERIFIED)

        profile_visibility = get_or_default(userdata, "profile_visibility", 0)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.add(
                    User(
                        id=user_id,
                        username=username,
                        email=email,
                        given_name=given_name,
                        family_name=family_name,
                        profile_image=profile_image,
                        authentication=auth.get_id(),
                        status=status.get_id(),
                        profile_visibility=profile_visibility,
                    )
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to add user") from exc

        if auth == UserAuthentication.DEFAULT:
            password = get_or_raise(
                userdata, "password", InvalidArgumentException("expected password")
            )
            self.set_password(user_id, password)

    def get_user_by_id(self, user_id: str):
        """
        Returns the `User` object whose ID matches the provided value.

        Args:
            user_id (str): The ID of the target user.

        Returns:
            The `User` object of the target user.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoUserException: If the passed ID does not correspond to
            any user in the database.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator(expire_on_commit=False) as session:
                user = session.query(User).filter_by(id=user_id).first()
                if user is None:
                    raise NoUserException(user_id)
                return user
        except NoUserException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_user_by_username(self, username: str):
        """
        Returns the `User` object whose username matches the provided value.

        Args:
            username (str): The username of the target user.

        Returns:
            The `User` object of the target user.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoUserException: If the passed username does not correspond to
            any user in the database.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator(expire_on_commit=False) as session:
                user = session.query(User).filter_by(username=username).first()
                if user is None:
                    raise NoUserException(username, "username")
                return user
        except NoUserException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_user(self, user_id: str):
        """
        Deletes the user with the specified ID.

        Args:
            user_id (str): The ID of the target user.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoUserException: If the passed ID does not correspond to any user in the database.
        """
        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.query(User).filter_by(id=user_id).delete()
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def user_exists(self, user_id: str) -> bool:
        """
        Returns true if a user exists with the specified ID.

        Args:
            user_id (str): The ID of the target user.

        Returns:
            True if the user exists and false otherwise.

        Raises:
            DatabaseException: If the function failed to query the database.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                return session.query(User).filter_by(id=user_id).first() is not None
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def add_users(self, userdata: list[dict]):
        """
        Creates new users with the specified user data.

        This is a bulk operation, which means it is equivalent to calling
        `add_user()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            userdata (list[dict]): The list of userdata dictionaries to use to create the users.
            The format of the dictionaries is specified under `add_user()`.

        Raises:
            DatabaseException: If the function failed to create the users.
            DuplicateUserException: If a user already exists in the database
            with any of the the specified IDs, usernames, or emails.
            InvalidArgumentException: If any of the provided arguments were invalid.
            EncryptionException: If the authentication method for any of the users is `DEFAULT`
            and the provided password was unable to be properly encrypted.
        """
        processed_data = []

        for i, user in enumerate(userdata):
            authentication = get_or_raise(
                user,
                "authentication",
                InvalidArgumentException(
                    f"expected authentication for user at index {i}"
                ),
            )
            email = get_or_raise(
                user,
                "email",
                InvalidArgumentException(f"expected email for user at index {i}"),
            )
            user_id = get_or_default_func(
                # pylint: disable=unnecessary-lambda
                # This lambda is necessary; we do not want the function to run
                # unless the key is not present
                user,
                "id",
                lambda: self.generate_user_id(),
            )
            username = get_or_default_func(
                # pylint: disable=unnecessary-lambda
                # This lambda is necessary; we do not want the function to run
                # unless the key is not present
                user,
                "username",
                lambda: self.generate_username(),
            )

            # We want to make sure we also check the users currently being processed
            # because those users can't contain duplicate emails, usernames, or IDs
            # in comparison to each other
            if self.email_exists(email) or dict_list_contains(
                processed_data, "email", email
            ):
                raise DuplicateUserException(email, "email")
            if self.username_exists(username) or dict_list_contains(
                processed_data, "username", username
            ):
                raise DuplicateUserException(username, "username")
            if self.user_exists(user_id) or dict_list_contains(
                processed_data, "user_id", user_id
            ):
                raise DuplicateUserException(user_id)

            Database.validate_email(email)
            Database.validate_username(username)
            Database.validate_user_id(user_id)

            processed_data.append(
                {
                    "id": user_id,
                    "username": username,
                    "email": email,
                    "given_name": get_or_default(user, "given_name", ""),
                    "family_name": get_or_default(user, "family_name", ""),
                    "profile_image": get_or_default(
                        user,
                        "profile_image",
                        "/static/assets/default_user_profile_image.png",
                    ),
                    "authentication": authentication,
                    "status": get_or_default(
                        user, "status", UserStatus.UNVERIFIED.get_id()
                    ),
                    "password": get_or_default(user, "password", None),
                    "profile_visibility": get_or_default(user, "profile_visibility", 0),
                }
            )

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                for user in processed_data:
                    session.add(
                        User(
                            id=user["id"],
                            username=user["username"],
                            email=user["email"],
                            given_name=user["given_name"],
                            family_name=user["family_name"],
                            profile_image=user["profile_image"],
                            authentication=user["authentication"],
                            status=user["status"],
                            profile_visibility=user["profile_visibility"],
                        )
                    )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to add users") from exc

        for user in processed_data:
            if user["authentication"] == UserAuthentication.DEFAULT.get_id():
                password = user["password"]
                if password is None:
                    raise InvalidArgumentException("expected password")
                self.set_password(user["id"], password)

    def get_users_by_id(self, user_ids: list[str]):
        """
        Returns a list of `User` objects whose IDs match the specified user IDs.

        This is a bulk operation, which means it is equivalent to calling
        `get_user_by_id()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            user_ids (list[str]): The IDs of the target users.

        Returns:
            A list of `User` objects whose IDs match the specified user IDs.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoUserException: If any of the passed IDs do not correspond to a user in the database.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator(expire_on_commit=False) as session:
                users = []
                for user_id in user_ids:
                    user = session.query(User).filter_by(id=user_id).first()
                    if user is None:
                        raise NoUserException(user_id)
                    users.append(user)
                return users
        except NoUserException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_users_by_username(self, usernames: list[str]):
        """
        Returns a list of `User` objects whose usernames match the specified usernames.

        This is a bulk operation, which means it is equivalent to calling
        `get_user_by_username()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            usernames (list[str]): The usernames of the target users.

        Returns:
            A list of `User` objects whose usernames match the specified usernames.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoUserException: If any of the passed usernames do not correspond
            to a user in the database.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator(expire_on_commit=False) as session:
                users = []
                for username in usernames:
                    user = session.query(User).filter_by(username=username).first()
                    if user is None:
                        raise NoUserException(username, "username")
                    users.append(user)
                return users
        except NoUserException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_users(self, user_ids: list[str]):
        """
        Deletes all of the users with the specified user IDs.

        This is a bulk operation, which means it is equivalent
        to calling `delete_user()` repeatedly, but this function
        is faster because it batches all of the operations into a single database call.

        Args:
            user_ids (list[str]): The IDs of the target users.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoUserException: If any of the passed IDs do not correspond to a user in the database.
        """
        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                for user_id in user_ids:
                    user = session.query(User).filter_by(id=user_id).first()
                    if user is None:
                        raise NoUserException(user_id)
                    session.delete(user)
                session.commit()
        except NoUserException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def search_users_by_name(
        self,
        query: str,
        offset: int = 0,
        limit: int = 10,
        obey_visibility_rules: bool = True,
    ):
        """
        Returns a list of `User` objects whose names contain the given query string
        and the maximum number of available results.

        Args:
            query (str): The query string to use when searching for users.
            offset (int): The offset into the search results to start at.
                This value is optional and is 0 by default.
            limit (int): The maximum number of users to return.
                This value is optional and is 10 by default.
            obey_visibility_rules (bool): Whether the visibility rules should be obeyed
                when searching for users, meaning that users whose names are not publicly
                visible will not show up in the search results if this value is true.
                This value is optional and is true by default.

        Returns:
            A tuple containing the list of `User` objects whose names contain
            the given query string, or an empty list if no users match the query,
            and an integer describing the maximum number of available results.

        Raises:
            DatabaseException: If the function failed to query the database.
            InvalidArgumentException: If the specified offset or limit was less than 0.
        """

        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")
        if offset < 0:
            raise InvalidArgumentException("expected offset >= 0")

        # Split the query into two parts (given name and family name)
        parts = query.strip().split(sep=None)
        name1 = parts[0] if len(parts) > 0 else query
        name2 = parts[1] if len(parts) > 1 else ""

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator(expire_on_commit=False) as session:
                filters = None
                if name2 == "":
                    filters = and_(
                        or_(
                            not obey_visibility_rules,
                            User.profile_visibility.op("&")(
                                ProfileVisibility.NAME.value
                            )
                            == ProfileVisibility.NAME.value,
                        ),
                        or_(
                            User.given_name.ilike(f"%{name1}%"),
                            User.family_name.ilike(f"%{name1}%"),
                        ),
                    )
                else:
                    filters = and_(
                        or_(
                            not obey_visibility_rules,
                            User.profile_visibility.op("&")(
                                ProfileVisibility.NAME.value
                            )
                            == ProfileVisibility.NAME.value,
                        ),
                        or_(
                            and_(
                                User.given_name.ilike(f"%{name1}%"),
                                User.family_name.ilike(f"%{name2}%"),
                            ),
                            and_(
                                User.given_name.ilike(f"%{name2}%"),
                                User.family_name.ilike(f"%{name1}%"),
                            ),
                        ),
                    )

                count = session.query(User).filter(filters).count()

                users = (
                    session.query(User)
                    .filter(filters)
                    .offset(offset)
                    .limit(limit)
                    .all()
                )

                if users is not None:
                    return (users, count)
                return ([], count)
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def search_users_by_username(self, query: str, offset: int = 0, limit: int = 10):
        """
        Returns a list of `User` objects whose usernames contain the given query string
        and the maximum number of available results.

        Args:
            query (str): The query string to use when searching for users.
            offset (int): The offset into the search results to start at.
                This value is optional and is 0 by default.
            limit (int): The maximum number of users to return.
                This value is optional and is 10 by default.

        Returns:
            A tuple containing the list of User objects whose usernames
            contain the given query string, or an empty list if no users match the query,
            and an integer describing the maximum number of available results.

        Raises:
            DatabaseException: If the function failed to query the database.
            InvalidArgumentException: If the specified offset or limit was less than 0.
        """

        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")
        if offset < 0:
            raise InvalidArgumentException("expected offset >= 0")

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator(expire_on_commit=False) as session:
                count = (
                    session.query(User)
                    .filter(User.username.ilike(f"%{query.strip()}%"))
                    .count()
                )

                users = (
                    session.query(User)
                    .filter(User.username.ilike(f"%{query.strip()}%"))
                    .offset(offset)
                    .limit(limit)
                    .all()
                )

                if users is not None:
                    return (users, count)
                return ([], count)
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    # ===== GLOBAL RECIPE INFO ===== #

    def add_recipe_info(self, info: dict):
        """
        Adds the recipe with the specified information to the database.

        Args:
            info (dict): A dictionary of recipe info values consisting
                of the following entries (required entries are listed first):
                id (int): The ID of the recipe.
                name (str): The name of the recipe.
                image (str): The URL of the recipe's image.
                    If it is not present, this function will automatically insert a default URL.
                summary (str): The (brief) summary for the recipe.
                    This value is optional.
                full_summary (str): The full summary for the recipe.
                    This value is optional.

        Raises:
            DatabaseException: If the function failed to add the recipe.
            DuplicateRecipeException: If a recipe already exists
            in the database with the specified ID.
            InvalidArgumentException: If any of the provided arguments were invalid.
        """

        recipe_id: int = get_or_raise(
            info, "id", InvalidArgumentException("expected id")
        )
        name = get_or_raise(info, "name", InvalidArgumentException("expected name"))
        image = get_or_default(info, "image", "/static/assets/default_recipe_image.png")
        summary = get_or_default(info, "summary", "")
        full_summary = get_or_default(info, "full_summary", "")

        if self.recipe_info_exists(recipe_id):
            raise DuplicateRecipeException(recipe_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Recipe

        try:
            with self.session_generator() as session:
                session.add(
                    Recipe(
                        id=recipe_id,
                        name=name,
                        image=image,
                        summary=summary,
                        full_summary=full_summary,
                    )
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_recipe_info(self, recipe_id: int):
        """
        Returns the `Recipe` object whose ID matches the provided ID.

        Args:
            recipe_id (int): The ID of the target recipe.

        Returns:
            The `Recipe` object whose ID matches the provided one.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoRecipeException: If no recipe exists with the specified ID.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Recipe

        try:
            with self.session_generator(expire_on_commit=False) as session:
                recipe = session.query(Recipe).filter_by(id=recipe_id).first()
                if recipe is None:
                    raise NoRecipeException(recipe_id)
                return recipe
        except NoRecipeException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_recipe_info(self, recipe_id: int):
        """
        Deletes the recipe whose ID matches the provided ID.

        Args:
            recipe_id (int): The ID of the target recipe.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoRecipeException: If no recipe exists with the specified ID.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Recipe

        try:
            with self.session_generator(expire_on_commit=False) as session:
                recipe = session.query(Recipe).filter_by(id=recipe_id).first()
                if recipe is None:
                    raise NoRecipeException(recipe_id)
                session.delete(recipe)
                session.commit()
        except NoRecipeException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def recipe_info_exists(self, recipe_id: int) -> bool:
        """
        Returns true if a recipe with the specified ID exists in the database.

        Args:
            recipe_id (int): The ID of the target recipe.

        Returns:
            True if a recipe with the specified ID exists in the database and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Recipe

        try:
            with self.session_generator() as session:
                return session.query(Recipe).filter_by(id=recipe_id).first() is not None
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def add_recipe_infos(self, infos: list[dict], ignore_duplicates: bool = False):
        """
        Adds multiple recipes to the database whose data is specified
        in the list of recipe information.

        This is a bulk operation, which means it is equivalent to calling
        `add_recipe_info()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            infos (list[dict]): The list of recipe information dictionaries
                to use to create the recipes. The format of the dictionaries
                is specified under `add_recipe_info()`.
            ignore_duplicates (bool): Whether this function should skip over duplicate recipes
                instead of raising an error. This value is optional and is false by default.

        Raises:
            DatabaseException: If the function failed to add the recipes.
            DuplicateRecipeException: If a recipe already exists in the database
            with any of the specified IDs.
            InvalidArgumentException: If any of the provided arguments were invalid.
        """
        processed_infos = []

        for i, info in enumerate(infos):
            recipe_id: int = get_or_raise(
                info, "id", InvalidArgumentException(f"expected id at index {i}")
            )
            name = get_or_raise(
                info, "name", InvalidArgumentException(f"expected name at index {i}")
            )
            image = get_or_default(
                info, "image", "/static/assets/default_recipe_image.png"
            )
            summary = get_or_default(info, "summary", "")
            full_summary = get_or_default(info, "full_summary", "")

            unique = not (
                dict_list_contains(processed_infos, "id", recipe_id)
                or self.recipe_info_exists(recipe_id)
            )

            if not unique and not ignore_duplicates:
                raise DuplicateRecipeException(recipe_id)

            if unique:
                processed_infos.append(
                    {
                        "id": recipe_id,
                        "name": name,
                        "image": image,
                        "summary": summary,
                        "full_summary": full_summary,
                    }
                )

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Recipe

        try:
            with self.session_generator() as session:
                for info in processed_infos:
                    session.add(
                        Recipe(
                            id=info["id"],
                            name=info["name"],
                            image=info["image"],
                            summary=info["summary"],
                            full_summary=info["full_summary"],
                        )
                    )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_recipe_infos(self, recipe_ids: list[int]):
        """
        Returns a list of `Recipe` objects whose IDs match the specified recipe IDs.

        This is a bulk operation, which means it is equivalent to calling
        `get_recipe_info()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            recipe_ids (list[int]): The IDs of the target recipes.

        Returns:
            A list of `Recipe` objects whose IDs match the specified recipe IDs.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoRecipeException: If any of the passed IDs do not correspond to
            a recipe in the database.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Recipe

        try:
            with self.session_generator(expire_on_commit=False) as session:
                recipes = []
                for recipe_id in recipe_ids:
                    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
                    if recipe is None:
                        raise NoRecipeException(recipe_id)
                    recipes.append(recipe)
                return recipes
        except NoRecipeException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_recipe_infos(self, recipe_ids: list[int]):
        """
        Deletes all of the recipes with the specified user IDs.

        This is a bulk operation, which means it is equivalent to calling
        `delete_recipe_infos()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            recipe_ids (list[int]): The IDs of the target recipes.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoRecipeException: If any of the passed IDs do not correspond to
            a recipe in the database.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Recipe

        try:
            with self.session_generator() as session:
                for recipe_id in recipe_ids:
                    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
                    if recipe is None:
                        raise NoRecipeException(recipe_id)
                    session.delete(recipe)
                session.commit()
        except NoRecipeException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_random_recipe_infos(self, limit: int = 10):
        """
        Returns a random list of recipes.

        Args:
            limit (int): The maximum number of results to return.
                This value is optional and is 10 by default.

        Returns:
            A random list of Recipe objects, or an empty list if there are
            no recipe objects in the database.

        Raises:
            DatabaseException: If the function failed to query the database.
            InvalidArgumentException: If the specified limit was less than 1.
        """
        if limit < 1:
            raise InvalidArgumentException("expected limit > 0")

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Recipe

        try:
            recipes = None
            with self.session_generator(expire_on_commit=False) as session:
                recipes = (
                    session.query(Recipe).order_by(func.random()).limit(limit).all()
                )

            if recipes is None:
                return []

            return [recipe.to_json() for recipe in recipes]
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    # ===== GLOBAL INGREDIENT INFO ===== #

    def add_ingredient_info(self, info: dict):
        """
        Adds the ingredient with the specified information to the database.

        Args:
            info (dict): A dictionary of ingredient info values consisting
                of the following entries (required entries are listed first):
                id (int): The ID of the ingredient.
                name (str): The name of the ingredient.
                image (str): The URL of the ingredient's image.
                    If it is not present, this function will automatically insert a default URL.

        Raises:
            DatabaseException: If the function failed to add the ingredient.
            DuplicateIngredientException: If a ingredient already exists
            in the database with the specified ID.
            InvalidArgumentException: If any of the provided arguments were invalid.
        """

        ingredient_id: int = get_or_raise(
            info, "id", InvalidArgumentException("expected id")
        )
        name = get_or_raise(info, "name", InvalidArgumentException("expected name"))
        image = get_or_default(
            info, "image", "/static/assets/default_ingredient_image.png"
        )

        if self.ingredient_info_exists(ingredient_id):
            raise DuplicateIngredientException(ingredient_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Ingredient

        try:
            with self.session_generator() as session:
                session.add(
                    Ingredient(
                        id=ingredient_id,
                        name=name,
                        image=image,
                    )
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_ingredient_info(self, ingredient_id: int):
        """
        Returns the `Ingredient` object whose ID matches the provided ID.

        Args:
            ingredient_id (int): The ID of the target ingredient.

        Returns:
            The `Ingredient` object whose ID matches the provided one.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoIngredientException: If no ingredient exists with the specified ID.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Ingredient

        try:
            with self.session_generator(expire_on_commit=False) as session:
                ingredient = (
                    session.query(Ingredient).filter_by(id=ingredient_id).first()
                )
                if ingredient is None:
                    raise NoIngredientException(ingredient_id)
                return ingredient
        except NoIngredientException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_ingredient_info(self, ingredient_id: int):
        """
        Deletes the ingredient whose ID matches the provided ID.

        Args:
            ingredient_id (int): The ID of the target ingredient.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoIngredientException: If no ingredient exists with the specified ID.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Ingredient

        try:
            with self.session_generator(expire_on_commit=False) as session:
                ingredient = (
                    session.query(Ingredient).filter_by(id=ingredient_id).first()
                )
                if ingredient is None:
                    raise NoIngredientException(ingredient_id)
                session.delete(ingredient)
                session.commit()
        except NoIngredientException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def ingredient_info_exists(self, ingredient_id: int) -> bool:
        """
        Returns true if a ingredient with the specified ID exists in the database.

        Args:
            ingredient_id (int): The ID of the target ingredient.

        Returns:
            True if a ingredient with the specified ID exists in the database and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Ingredient

        try:
            with self.session_generator() as session:
                return (
                    session.query(Ingredient).filter_by(id=ingredient_id).first()
                    is not None
                )
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def add_ingredient_infos(self, infos: list[dict], ignore_duplicates: bool = False):
        """
        Adds multiple ingredients to the database whose data is specified
        in the list of ingredient information.

        This is a bulk operation, which means it is equivalent to calling
        `add_ingredient_info()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            infos (list[dict]): The list of ingredient information dictionaries
                to use to create the ingredients. The format of the dictionaries
                is specified under `add_ingredient_info()`.
            ignore_duplicates (bool): Whether this function should skip over duplicate ingredients
                instead of raising an error. This value is optional and is false by default.

        Raises:
            DatabaseException: If the function failed to add the ingredients.
            DuplicateIngredientException: If a ingredient already exists in the database
            with any of the specified IDs.
            InvalidArgumentException: If any of the provided arguments were invalid.
        """
        processed_infos = []

        for i, info in enumerate(infos):
            ingredient_id: int = get_or_raise(
                info, "id", InvalidArgumentException(f"expected id at index {i}")
            )
            name = get_or_raise(
                info, "name", InvalidArgumentException(f"expected name at index {i}")
            )
            image = get_or_default(
                info, "image", "/static/assets/default_ingredient_image.png"
            )

            unique = not (
                dict_list_contains(processed_infos, "id", ingredient_id)
                or self.ingredient_info_exists(ingredient_id)
            )

            if not unique and not ignore_duplicates:
                raise DuplicateIngredientException(ingredient_id)

            if unique:
                processed_infos.append(
                    {
                        "id": ingredient_id,
                        "name": name,
                        "image": image,
                    }
                )

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Ingredient

        try:
            with self.session_generator() as session:
                for info in processed_infos:
                    session.add(
                        Ingredient(
                            id=info["id"],
                            name=info["name"],
                            image=info["image"],
                        )
                    )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_ingredient_infos(self, ingredient_ids: list[int]):
        """
        Returns a list of `Ingredient` objects whose IDs match the specified ingredient IDs.

        This is a bulk operation, which means it is equivalent to calling
        `get_ingredient_info()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            ingredient_ids (list[int]): The IDs of the target ingredients.

        Returns:
            A list of `Ingredient` objects whose IDs match the specified ingredient IDs.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoIngredientException: If any of the passed IDs do not correspond to
            a ingredient in the database.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Ingredient

        try:
            with self.session_generator(expire_on_commit=False) as session:
                ingredients = []
                for ingredient_id in ingredient_ids:
                    ingredient = (
                        session.query(Ingredient).filter_by(id=ingredient_id).first()
                    )
                    if ingredient is None:
                        raise NoIngredientException(ingredient_id)
                    ingredients.append(ingredient)
                return ingredients
        except NoIngredientException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_ingredient_infos(self, ingredient_ids: list[int]):
        """
        Deletes all of the ingredients with the specified user IDs.

        This is a bulk operation, which means it is equivalent to calling
        `delete_ingredient_infos()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args:
            ingredient_ids (list[int]): The IDs of the target ingredients.

        Raises:
            DatabaseException: If the function failed to query the database.
            NoIngredientException: If any of the passed IDs do not correspond to
            a ingredient in the database.
        """

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Ingredient

        try:
            with self.session_generator() as session:
                for ingredient_id in ingredient_ids:
                    ingredient = (
                        session.query(Ingredient).filter_by(id=ingredient_id).first()
                    )
                    if ingredient is None:
                        raise NoIngredientException(ingredient_id)
                    session.delete(ingredient)
                session.commit()
        except NoIngredientException as exc:
            raise exc
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    # ===== FRIENDS ===== #

    def add_relationship(self, user1_id: str, user2_id: str):
        """
        Adds a new relationship between the specified users.

        If the two specified users already have a relationship,
        this function has no effect.

        Args:
            user1_id (str): The ID of the first user in the relationship.
            user2_id (str): The ID of the second user in the relationship.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If either of the specified users do not exist.
        """

        if self.has_relationship(user1_id, user2_id):
            return  # Do nothing if the relationship already exists

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Relationship

        try:
            with self.session_generator() as session:
                session.add(Relationship(user1=user1_id, user2=user2_id))
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def has_relationship(self, user1_id: str, user2_id: str) -> bool:
        """
        Returns true if the specified users have a relationship.

        Args:
            user1_id (str): The ID of the first user in the relationship.
            user2_id (str): The ID of the second user in the relationship.

        Returns:
            True if the specified users have a relationship and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If either of the specified users do not exist.
        """

        if not self.user_exists(user1_id):
            raise NoUserException(user1_id)
        if not self.user_exists(user2_id):
            raise NoUserException(user2_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Relationship

        try:
            with self.session_generator() as session:
                return (
                    session.query(Relationship)
                    .filter(
                        or_(
                            and_(
                                Relationship.user1 == user1_id,
                                Relationship.user2 == user2_id,
                            ),
                            and_(
                                Relationship.user1 == user2_id,
                                Relationship.user2 == user1_id,
                            ),
                        )
                    )
                    .first()
                    is not None
                )
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_relationship(self, user1_id: str, user2_id: str):
        """
        Deletes the relationship for the specified users.

        If the specified users do not have a relationship, this function has no effect.

        Args:
            user1_id (str): The ID of the first user in the relationship.
            user2_id (str): The ID of the second user in the relationship.

        Returns:
            True if the relationship was deleted and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If either of the specified users do not exist.
        """

        if not self.user_exists(user1_id):
            raise NoUserException(user1_id)
        if not self.user_exists(user2_id):
            raise NoUserException(user2_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Relationship

        try:
            with self.session_generator() as session:
                relationship = (
                    session.query(Relationship)
                    .filter(
                        or_(
                            and_(
                                Relationship.user1 == user1_id,
                                Relationship.user2 == user2_id,
                            ),
                            and_(
                                Relationship.user1 == user2_id,
                                Relationship.user2 == user1_id,
                            ),
                        )
                    )
                    .first()
                )

                if relationship is not None:
                    session.delete(relationship)
                    session.commit()
                    return True
                return False
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_relationships_for_user(self, user_id: str, offset: int = 0, limit: int = 0):
        """
        Returns a list of `User` objects who have relationships with the
        specified user and the maximum number of available results.

        Args:
            user_id (str): The ID of the target user.
            offset (int): The offset into the results to start at.
                This value is optional and by default is 0.
            limit (int): The maximum number of results to return.
                This value is optional and by default is 0,
                which tells the database to return all available results.

        Returns:
            A tuple containing the list of User objects who have relationships
            with the specified user and an integer describing the maximum number
            of available results.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified offset or limit is less than 0.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        if offset < 0:
            raise InvalidArgumentException("expected offset >= 0")
        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Relationship

        try:
            with self.session_generator(expire_on_commit=False) as session:
                result = []

                first_user = session.query(Relationship).filter_by(user1=user_id).all()

                if first_user is not None:
                    for user in first_user:
                        result.append(user.user2_obj)

                second_user = session.query(Relationship).filter_by(user2=user_id).all()

                if second_user is not None:
                    for user in second_user:
                        result.append(user.user1_obj)

                count = len(result)

                if limit == 0:
                    return (result[offset:], count)
                return (result[offset : offset + limit], count)
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def add_friend_request(self, src: str, target: str) -> bool:
        """
        Adds a friend request from the source user to the target user.

        If a friend request has already been sent from the specified source user
        to the specified target user, this function has no effect.

        Args:
            src (str): The ID of the user who sent the request.
            target (str): The ID of the user who will receive the request.

        Returns:
            True if the friend request was added and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If either of the specified users do not exist.
        """

        if not self.user_exists(src):
            raise NoUserException(src)
        if not self.user_exists(target):
            raise NoUserException(target)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import FriendRequest

        try:
            with self.session_generator() as session:
                request = (
                    session.query(FriendRequest)
                    .filter_by(src=src, target=target)
                    .first()
                )

                if request is not None:
                    return False
                session.add(FriendRequest(src=src, target=target))
                session.commit()
                return True
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_friend_requests_for_source(self, src: str, offset: int = 0, limit: int = 0):
        """
        Returns a list of User objects which are targets for friend requests
        from the specified source user and the maximum number of available results.

        Args:
            src (str): The ID of the user who sent the requests.
            offset (int): The offset into the results to start at.
                This value is optional and by default is 0.
            limit (int): The maximum number of results to return.
                This value is optional and by default is 0,
                which tells the database to return all available results.

        Returns:
            A tuple containing the list of User objects which are targets for friend requests
            from the specified source user and an integer describing the maximum number
            of available results.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified offset or limit is less than 0.
        """

        if not self.user_exists(src):
            raise NoUserException(src)

        if offset < 0:
            raise InvalidArgumentException("expected offset >= 0")
        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import FriendRequest

        try:
            with self.session_generator(expire_on_commit=False) as session:
                result = []

                count = session.query(FriendRequest).filter_by(src=src).count()

                requests = (
                    session.query(FriendRequest).filter_by(src=src).offset(offset)
                )

                if limit == 0:
                    requests = requests.all()
                else:
                    requests = requests.limit(limit).all()

                if requests is not None:
                    for request in requests:
                        result.append(request.target_obj)
                return (result, count)
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_friend_requests_for_target(
        self, target: str, offset: int = 0, limit: int = 0
    ):
        """
        Returns a list of User objects which are sources
        for friend requests to the specified target user
        and the maximum number of available results.

        Args:
            target (str): The ID of the user who received the requests.
            offset (int): The offset into the results to start at.
                This value is optional and by default is 0.
            limit (int): The maximum number of results to return.
                This value is optional and by default is 0,
                which tells the database to return all available results.

        Returns:
            A tuple containing the list of User objects which are sources
            for friend requests to the specified target user
            and an integer describing the maximum number
            of available results.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """

        if not self.user_exists(target):
            raise NoUserException(target)

        if offset < 0:
            raise InvalidArgumentException("expected offset >= 0")
        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import FriendRequest

        try:
            with self.session_generator(expire_on_commit=False) as session:
                result = []

                count = session.query(FriendRequest).filter_by(target=target).count()

                requests = (
                    session.query(FriendRequest).filter_by(target=target).offset(offset)
                )

                if limit == 0:
                    requests = requests.all()
                else:
                    requests = requests.limit(limit).all()

                if requests is not None:
                    for request in requests:
                        result.append(request.src_obj)
                return (result, count)
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_friend_request(self, src: str, target: str) -> bool:
        """
        Deletes the friend request for the specified source and target users.

        If a friend request does not exist between specified source user
        and the specified target user, this function has no effect.

        Args:
            src (str): The ID of the user who sent the request.
            target (str): The ID of the user who received the request.

        Returns:
            True if the friend request was deleted and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If either of the specified users do not exist.
        """

        if not self.user_exists(src):
            raise NoUserException(src)
        if not self.user_exists(target):
            raise NoUserException(target)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import FriendRequest

        try:
            with self.session_generator() as session:
                request = (
                    session.query(FriendRequest)
                    .filter_by(src=src, target=target)
                    .first()
                )

                if request is None:
                    return False
                session.delete(request)
                session.commit()
                return True
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    # ===== USER INTOLERANCES ===== #

    def add_intolerance(self, user_id: str, intolerance: UserIntolerance) -> bool:
        """
        Adds the specified intolerance to the specified user.

        If the user already has the specified intolerance, this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            intolerance (UserIntolerance): The target intolerance value.

        Returns:
            True if the intolerance was added and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """

        if self.has_intolerance(user_id, intolerance):
            return False  # Do nothing if it's already present

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Intolerance

        try:
            with self.session_generator() as session:
                session.add(Intolerance(user_id=user_id, intolerance=intolerance.value))
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

        return True

    def has_intolerance(self, user_id: str, intolerance: UserIntolerance) -> bool:
        """
        Returns true if the user has the specified intolerance.

        Args:
            user_id (str): The ID of the target user.
            intolerance (UserIntolerance): The target intolerance value.

        Returns:
            True if the user has the specified intolerance and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Intolerance

        try:
            with self.session_generator() as session:
                return (
                    session.query(Intolerance)
                    .filter_by(user_id=user_id, intolerance=intolerance.value)
                    .first()
                    is not None
                )
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_intolerance(self, user_id: str, intolerance: UserIntolerance) -> bool:
        """
        Deletes the specified intolerance from the user's list of intolerances.

        If the user does not have the specified intolerance, this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            intolerance (UserIntolerance): The target intolerance value.

        Returns:
            True if the intolerance was deleted and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Intolerance

        try:
            with self.session_generator() as session:
                entry = (
                    session.query(Intolerance)
                    .filter_by(user_id=user_id, intolerance=intolerance.value)
                    .first()
                )
                if entry is not None:
                    session.delete(entry)
                    session.commit()
                    return True
                return False
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_intolerances(
        self, user_id: str, offset: int = 0, limit: int = 0
    ) -> tuple[list[UserIntolerance], int]:
        """
        Returns a list of intolerances for the specified user.

        Args:
            user_id (str): The ID of the target user.
            offset (int): The offset into the results to start at.
                This value is optional and by default is 0.
            limit (int): The maximum number of results to return.
                This value is optional and by default is 0,
                which tells the database to return all available results.

        Returns:
            A tuple containing the list of intolerances for the specified user,
            or an empty list if the user has no intolerances and an integer
            describing the maximum number of available results.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified offset or limit is less than 0.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        if offset < 0:
            raise InvalidArgumentException("expected offset >= 0")
        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import Intolerance

        try:
            with self.session_generator(expire_on_commit=False) as session:
                result = []
                count = session.query(Intolerance).filter_by(user_id=user_id).count()
                intolerances = (
                    session.query(Intolerance).filter_by(user_id=user_id).offset(offset)
                )

                if limit == 0:
                    intolerances = intolerances.all()
                else:
                    intolerances = intolerances.limit(limit).all()

                if intolerances is not None:
                    for entry in intolerances:
                        result.append(UserIntolerance.get_from_id(entry.intolerance))
                return (result, count)
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    # ===== USER-SAVED RECIPES ===== #

    def add_recipe(self, user_id: str, recipe_info: dict) -> bool:
        """
        Adds the specified recipe to the user's list of saved recipes.

        If the user already has the recipe saved, this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            recipe_info (dict): The info for the target recipe.
                The format for this argument is specified in the `add_recipe_info()` section.
                If the specified recipe does not exist in the global recipe table,
                this function will add it to the table.

        Returns:
            True if the recipe was added and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If any of the provided arguments were invalid.
        """

        recipe_id: int = get_or_raise(
            recipe_info, "id", InvalidArgumentException("expected id")
        )

        if self.has_recipe(user_id, recipe_id):
            return False  # Do nothing if it's already present

        if not self.recipe_info_exists(recipe_id):
            self.add_recipe_info(recipe_info)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedRecipe

        try:
            with self.session_generator() as session:
                session.add(SavedRecipe(user_id=user_id, recipe_id=recipe_id))
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

        return True

    def has_recipe(self, user_id: str, recipe_id: int) -> bool:
        """
        Returns true if the user already has the specified recipe saved in their list of recipes.

        Args:
            user_id (str): The ID of the target user.
            recipe_id (int): The ID for the target recipe.

        Returns:
            True if the user already has the specified recipe saved
            in their list of recipes and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedRecipe

        try:
            with self.session_generator() as session:
                return (
                    session.query(SavedRecipe)
                    .filter_by(user_id=user_id, recipe_id=recipe_id)
                    .first()
                    is not None
                )
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_recipe(self, user_id: str, recipe_id: int) -> bool:
        """
        Deletes the recipe from the user's list of saved recipes.

        If the user does not have the specified recipe in their list,
        this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            recipe_id (int): The ID for the target recipe.

        Returns:
            True if the recipe was deleted and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedRecipe

        try:
            with self.session_generator() as session:
                entry = (
                    session.query(SavedRecipe)
                    .filter_by(user_id=user_id, recipe_id=recipe_id)
                    .first()
                )
                if entry is not None:
                    session.delete(entry)
                    session.commit()
                    return True
                return False
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_recipes(self, user_id: str, offset: int = 0, limit: int = 0):
        """
        Returns a list of Recipe objects for which the user has in their list of saved recipes.

        Args:
            user_id (str): The ID of the target user.
            offset (int): The offset into the results to start at.
                This value is optional and by default is 0.
            limit (int): The maximum number of results to return.
                This value is optional and by default is 0,
                which tells the database to return all available results.

        Returns:
            A tuple containing the list of Recipe objects for which the user
            has in their list of saved recipes, or an empty list if the user has no saved recipes,
            and an integer describing the maximum number of available results.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified offset or limit is less than 0.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        if offset < 0:
            raise InvalidArgumentException("expected offset >= 0")
        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedRecipe

        try:
            with self.session_generator(expire_on_commit=False) as session:
                result = []
                count = session.query(SavedRecipe).filter_by(user_id=user_id).count()
                entries = (
                    session.query(SavedRecipe).filter_by(user_id=user_id).offset(offset)
                )

                if limit == 0:
                    entries = entries.all()
                else:
                    entries = entries.limit(limit).all()

                if entries is not None:
                    for entry in entries:
                        result.append(entry.recipe)
                return (result, count)
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def add_recipes(self, user_ids: list[str], recipe_infos: list[dict]):
        """
        Adds each of the specified recipes to their corresponding user.

        For any of the user/recipe combinations,
        if the user already has the specified recipe,
        this function has no effect for that particular combination.

        This is a bulk operation, which means it is equivalent to calling
        `add_recipe()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args
            user_ids (list[str]): The list of user IDs.
                This list must have the same length as recipe_infos.
            recipe_infos (list[dict]): The list of recipe information dictionaries
                whose format is specified in `add_recipe()`.
                This list must have the same length as user_ids.

        Raises
            DatabaseException: If there was a problem querying the database.
            NoUserException: If any of the specified users do not exist.
            InvalidArgumentException: If any of the provided arguments are invalid.
        """
        if len(user_ids) != len(recipe_infos):
            raise InvalidArgumentException(
                "user_ids and recipe_infos must have the same length"
            )

        processed_user_ids = []
        recipe_ids = []

        for i, info in enumerate(recipe_infos):
            recipe_id: int = get_or_raise(
                info, "id", InvalidArgumentException("expected id")
            )
            user_id = user_ids[i]

            if not self.has_recipe(user_id, recipe_id):
                # Only add it to the list if the user doesn't already have it
                processed_user_ids.append(user_id)
                recipe_ids.append(recipe_id)

            if not self.recipe_info_exists(recipe_id):
                self.add_recipe_info(info)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedRecipe

        try:
            with self.session_generator() as session:
                for i, recipe_id in enumerate(recipe_ids):
                    session.add(SavedRecipe(user_id=user_ids[i], recipe_id=recipe_id))
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_recipes(self, user_ids: list[str], recipe_ids: list[int]):
        """
        Deletes all of the specified user and recipe combinations.

        For any of the user/recipe combinations,
        if the user does not have the specified recipe,
        this function has no effect for that particular combination.

        This is a bulk operation, which means it is equivalent to
        calling `delete_recipe()` repeatedly, but this function is faster
        because it batches all of the operations into a single database call.

        Args:
            user_ids (list[str]): The list of user IDs.
                This list must have the same length as recipe_ids.
            recipe_ids (list[int]): The list of recipe IDs.
                This list must have the same length as user_ids.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If any of the specified users do not exist.
        """

        if len(user_ids) != len(recipe_ids):
            raise InvalidArgumentException(
                "user_ids and recipe_ids must have the same length"
            )

        for user_id in user_ids:
            if not self.user_exists(user_id):
                raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedRecipe

        try:
            with self.session_generator() as session:
                for i, recipe_id in enumerate(recipe_ids):
                    recipe = (
                        session.query(SavedRecipe)
                        .filter_by(user_id=user_ids[i], recipe_id=recipe_id)
                        .first()
                    )
                    if recipe is not None:
                        session.delete(recipe)
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_user_top_recipes(self, user_id: str, limit: int = 5):
        """
        Returns a list of a random selection from the user's most recently liked recipes.

        The algorithm will look at only the most recently liked recipes
        and will only retrieve up to the specified limit of recipes.

        Args:
            user_id (str): The ID of the target user.
            limit (int): The maximum number of recipes to return.
                This value is optional and is 5 by default.

        Returns:
            A list of a random selection from the user's most recently liked recipes,
            or an empty list if the user has no saved recipes.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified limit is less than 0.
        """
        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")

        recipes = self.get_recipes(user_id)[0]

        result = {}

        recipes_len = len(recipes)

        recipe_count = min(limit, recipes_len)

        # The max number of tries the algorithm will do to find a
        # new recipe before it gives up on the current iteration
        max_tries = 10

        for _ in range(0, recipe_count):
            # The algorithm starts trying to sample from
            # the first recipe_count number of recipes and incrementally
            # increases its search range until it equals the length of the original list.
            current_range = recipe_count

            # We sample from the end of the list because
            # that's where the most recent recipes are
            index = randrange(recipes_len - current_range, recipes_len)

            tries = 0
            while recipes[index].id in result and tries <= max_tries:
                # Increase the search range if it's still less than the length of the actual list
                if current_range < recipe_count:
                    current_range += 1
                index = randrange(recipes_len - current_range, recipes_len)
                tries += 1
            if recipes[index].id in result:
                continue
            result[recipes[index].id] = recipes[index]

        return list(result.values())

    def get_friend_top_recipes(
        self, user_id: str, friend_limit: int = 5, limit_per_friend: int = 5
    ):
        """
        Returns a list of user/recipe list pairs generated based off
        of the liked recipes of the specified user's friends.

        The algorithm will look at only the most recently liked recipes
        and will only retrieve up to the specified limit of recipes per friend.

        Args:
            user_id (str): The ID of the target user.
            friend_limit (int): The maximum number of friends to look at.
                This value is optional and is 5 by default.
            limit_per_friend (int): The maximum number of recipes to retrieve per friend.
                This value is optional and is 5 by default.

        Returns:
            A list of user/recipe list pairs generated based off of the
            liked recipes of the specified user's friends, or an empty list
            if the user has no friends.

            Each entry in the list is a dictionary containing the following entries:
                user (User): The User object for the associated friend.
                recipes (list[Recipe]): The list of Recipe objects retrieved from
                    the associated friend's list of liked recipes.
                    This list will be empty if the associated friend has no saved recipes.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If either of the limit values are less than 0.
        """
        if friend_limit < 0:
            raise InvalidArgumentException("expected friend_limit >= 0")
        if limit_per_friend < 0:
            raise InvalidArgumentException("expected limit_per_friend >= 0")

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        processed_friend_ids = []
        result = []

        friends = self.get_relationships_for_user(user_id)

        friend_count = min(len(friends), friend_limit)

        # The max number of tries the algorithm will do to find
        # a new friend before it gives up on the current iteration
        max_tries = 10

        for _ in range(0, friend_count):
            index = randrange(len(friends))
            tries = 0
            while friends[index].id in processed_friend_ids and tries <= max_tries:
                index = randrange(len(friends))
                tries += 1
            if friends[index].id in processed_friend_ids:
                continue
            recipes = self.get_user_top_recipes(friends[index], limit_per_friend)
            result.append({"user": friends[index], "recipes": recipes})
            processed_friend_ids.append(friends[index].id)

        return result

    # ===== USER-SAVED INGREDIENTS ===== #

    def add_ingredient(
        self, user_id: str, ingredient_info: dict, liked: bool = True
    ) -> bool:
        """
        Adds the specified ingredient to the user's list of saved ingredients.

        If the user already has the ingredient saved, this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            ingredient_info (dict): The info for the target ingredient.
                The format for this argument is specified in the `add_ingredient_info()` section.
                If the specified ingredient does not exist in the global ingredient table,
                this function will add it to the table.
            liked (bool): Whether the user likes the ingredient. This value is optional and
                is true by default.

        Returns:
            True if the ingredient was added and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If any of the provided arguments were invalid.
        """

        ingredient_id: int = get_or_raise(
            ingredient_info, "id", InvalidArgumentException("expected id")
        )

        if self.has_ingredient(user_id, ingredient_id):
            return False  # Do nothing if it's already present

        if not self.ingredient_info_exists(ingredient_id):
            self.add_ingredient_info(ingredient_info)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedIngredient

        try:
            with self.session_generator() as session:
                session.add(
                    SavedIngredient(
                        user_id=user_id, ingredient_id=ingredient_id, liked=liked
                    )
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

        return True

    def has_ingredient(self, user_id: str, ingredient_id: int) -> bool:
        """
        Returns true if the user already has the specified ingredient
        saved in their list of ingredients.

        Args:
            user_id (str): The ID of the target user.
            ingredient_id (int): The ID for the target ingredient.

        Returns:
            True if the user already has the specified ingredient saved
            in their list of ingredients and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedIngredient

        try:
            with self.session_generator() as session:
                return (
                    session.query(SavedIngredient)
                    .filter_by(user_id=user_id, ingredient_id=ingredient_id)
                    .first()
                    is not None
                )
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_ingredient(self, user_id: str, ingredient_id: int) -> bool:
        """
        Deletes the ingredient from the user's list of saved ingredients.

        If the user does not have the specified ingredient in their list,
        this function has no effect.

        Args:
            user_id (str): The ID of the target user.
            ingredient_id (int): The ID for the target ingredient.

        Returns:
            True if the ingredient was deleted and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedIngredient

        try:
            with self.session_generator() as session:
                entry = (
                    session.query(SavedIngredient)
                    .filter_by(user_id=user_id, ingredient_id=ingredient_id)
                    .first()
                )
                if entry is not None:
                    session.delete(entry)
                    session.commit()
                    return True
                return False
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_ingredients(self, user_id: str, offset: int = 0, limit: int = 0):
        """
        Returns a list of Ingredient objects for which the user has
        in their list of saved ingredients.

        Args:
            user_id (str): The ID of the target user.
            offset (int): The offset into the results to start at.
                This value is optional and by default is 0.
            limit (int): The maximum number of results to return.
                This value is optional and by default is 0,
                which tells the database to return all available results.

        Returns:
            A tuple containing the list of Ingredient objects for which the user has
            in their list of saved ingredients (or an empty list if the user
            has no saved ingredients), a list of booleans describing whether the user
            likes the associated ingredient, and an integer describing the maximum number
            of available results.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified offset or limit is less than 0.
        """

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        if offset < 0:
            raise InvalidArgumentException("expected offset >= 0")
        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedIngredient

        try:
            with self.session_generator(expire_on_commit=False) as session:
                result = []
                liked = []
                count = (
                    session.query(SavedIngredient).filter_by(user_id=user_id).count()
                )
                entries = (
                    session.query(SavedIngredient)
                    .filter_by(user_id=user_id)
                    .offset(offset)
                )

                if limit == 0:
                    entries = entries.all()
                else:
                    entries = entries.limit(limit).all()

                if entries is not None:
                    for entry in entries:
                        result.append(entry.ingredient)
                        liked.append(entry.liked)
                return (result, liked, count)
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def add_ingredients(
        self, user_ids: list[str], ingredient_infos: list[dict], liked: list[bool]
    ):
        """
        Adds each of the specified ingredients to their corresponding user.

        For any of the user/ingredient combinations,
        if the user already has the specified ingredient,
        this function has no effect for that particular combination.

        This is a bulk operation, which means it is equivalent to calling
        `add_ingredient()` repeatedly, but this function is faster because
        it batches all of the operations into a single database call.

        Args
            user_ids (list[str]): The list of user IDs.
                This list must have the same length as ingredient_infos.
            ingredient_infos (list[dict]): The list of ingredient information dictionaries
                whose format is specified in `add_ingredient()`.
                This list must have the same length as `user_ids`.
            liked (list[bool]): The list of `liked` flags for each ingredient.
                This list must have the same length as `user_ids`.

        Raises
            DatabaseException: If there was a problem querying the database.
            NoUserException: If any of the specified users do not exist.
            InvalidArgumentException: If any of the provided arguments are invalid.
        """
        if len(user_ids) != len(ingredient_infos):
            raise InvalidArgumentException(
                "user_ids and ingredient_infos must have the same length"
            )

        processed_user_ids = []
        ingredient_ids = []
        processed_liked = []

        for i, info in enumerate(ingredient_infos):
            ingredient_id: int = get_or_raise(
                info, "id", InvalidArgumentException("expected id")
            )
            user_id = user_ids[i]

            if not self.has_ingredient(user_id, ingredient_id):
                # Only add it to the list if the user doesn't already have it
                processed_user_ids.append(user_id)
                ingredient_ids.append(ingredient_id)
                processed_liked.append(liked[i])

            if not self.ingredient_info_exists(ingredient_id):
                self.add_ingredient_info(info)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedIngredient

        try:
            with self.session_generator() as session:
                for i, ingredient_id in enumerate(ingredient_ids):
                    session.add(
                        SavedIngredient(
                            user_id=user_ids[i],
                            ingredient_id=ingredient_id,
                            liked=processed_liked[i],
                        )
                    )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def delete_ingredients(self, user_ids: list[str], ingredient_ids: list[int]):
        """
        Deletes all of the specified user and ingredient combinations.

        For any of the user/ingredient combinations,
        if the user does not have the specified ingredient,
        this function has no effect for that particular combination.

        This is a bulk operation, which means it is equivalent to
        calling `delete_ingredient()` repeatedly, but this function is faster
        because it batches all of the operations into a single database call.

        Args:
            user_ids (list[str]): The list of user IDs.
                This list must have the same length as ingredient_ids.
            ingredient_ids (list[int]): The list of ingredient IDs.
                This list must have the same length as user_ids.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If any of the specified users do not exist.
        """

        if len(user_ids) != len(ingredient_ids):
            raise InvalidArgumentException(
                "user_ids and ingredient_ids must have the same length"
            )

        for user_id in user_ids:
            if not self.user_exists(user_id):
                raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import SavedIngredient

        try:
            with self.session_generator() as session:
                for i, ingredient_id in enumerate(ingredient_ids):
                    ingredient = (
                        session.query(SavedIngredient)
                        .filter_by(user_id=user_ids[i], ingredient_id=ingredient_id)
                        .first()
                    )
                    if ingredient is not None:
                        session.delete(ingredient)
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def get_user_top_ingredients(self, user_id: str, limit: int = 5):
        """
        Returns a list of a random selection from the user's most recently liked ingredients.

        The algorithm will look at only the most recently liked ingredients
        and will only retrieve up to the specified limit of ingredients.

        Args:
            user_id (str): The ID of the target user.
            limit (int): The maximum number of ingredients to return.
                This value is optional and is 5 by default.

        Returns:
            A list of a random selection from
            the user's most recently liked ingredients,
            or an empty list if the user has no saved ingredients.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified offset or limit is less than 0.
        """
        if limit < 0:
            raise InvalidArgumentException("expected limit >= 0")

        ingredients = self.get_ingredients(user_id)[0]

        result = {}

        ingredients_len = len(ingredients)

        ingredient_count = min(limit, ingredients_len)

        # The max number of tries the algorithm will do to find a
        # new ingredient before it gives up on the current iteration
        max_tries = 10

        for _ in range(0, ingredient_count):
            # The algorithm starts trying to sample from
            # the first ingredient_count number of ingredients and incrementally
            # increases its search range until it equals the length of the original list.
            current_range = ingredient_count

            # We sample from the end of the list because
            # that's where the most recent ingredients are
            index = randrange(ingredients_len - current_range, ingredients_len)

            tries = 0
            while ingredients[index].id in result and tries <= max_tries:
                # Increase the search range if it's still less than the length of the actual list
                if current_range < ingredient_count:
                    current_range += 1
                index = randrange(ingredients_len - current_range, ingredients_len)
                tries += 1
            if ingredients[index].id in result:
                continue
            result[ingredients[index].id] = ingredients[index]

        return list(result.values())

    def get_friend_top_ingredients(
        self, user_id: str, friend_limit: int = 5, limit_per_friend: int = 5
    ):
        """
        Returns a list of user/ingredient list pairs generated based off
        of the liked ingredients of the specified user's friends.

        The algorithm will look at only the most recently liked ingredients
        and will only retrieve up to the specified limit of ingredients per friend.

        Args:
            user_id (str): The ID of the target user.
            friend_limit (int): The maximum number of friends to look at.
                This value is optional and is 5 by default.
            limit_per_friend (int): The maximum number of ingredients to retrieve per friend.
                This value is optional and is 5 by default.

        Returns:
            A list of user/ingredient list pairs generated based off of the
            liked ingredients of the specified user's friends, or an empty list
            if the user has no friends.

            Each entry in the list is a dictionary containing the following entries:
                user (User): The User object for the associated friend.
                ingredients (list[Ingredient]): The list of Ingredient objects retrieved from
                    the associated friend's list of liked ingredients.
                    This list will be empty if the associated friend has no saved ingredients.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If either of the limit values are less than 0.
        """
        if friend_limit < 0:
            raise InvalidArgumentException("expected friend_limit >= 0")
        if limit_per_friend < 0:
            raise InvalidArgumentException("expected limit_per_friend >= 0")

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        processed_friend_ids = []
        result = []

        friends = self.get_relationships_for_user(user_id)

        friend_count = min(len(friends), friend_limit)

        # The max number of tries the algorithm will do to find
        # a new friend before it gives up on the current iteration
        max_tries = 10

        for _ in range(0, friend_count):
            index = randrange(len(friends))
            tries = 0
            while friends[index].id in processed_friend_ids and tries <= max_tries:
                index = randrange(len(friends))
                tries += 1
            if friends[index].id in processed_friend_ids:
                continue
            ingredients = self.get_user_top_ingredients(
                friends[index], limit_per_friend
            )
            result.append({"user": friends[index], "ingredients": ingredients})
            processed_friend_ids.append(friends[index].id)

        return result

    # ===== USER ACCOUNT MANAGEMENT ===== #

    def set_username(self, user_id: str, username: str):
        """
        Sets the username for the specified user.

        Args:
            user_id (str): The ID of the target user.
            username (str): The username for the target user.
                This value must be unique across all users and must
                conform to the syntax rules specified in the users table.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            DuplicateUserException: If the specified username is already taken.
            InvalidArgumentException: If the specified username is syntactically invalid.
        """
        Database.validate_username(username)

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.query(User).filter_by(id=user_id).update({"username": username})
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def set_email(self, user_id: str, email: str):
        """
        Sets the email for the specified user.

        Args:
            user_id (str): The ID of the target user.
            email (str): The email for the target user.
                This value must be unique across all users and
                must conform to regular email syntax rules.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            DuplicateUserException: If the specified email is already taken.
            InvalidArgumentException: If the specified email is syntactically invalid.
        """
        Database.validate_email(email)

        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.query(User).filter_by(id=user_id).update({"email": email})
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def set_password(self, user_id: str, password: str, encrypted: bool = False):
        """
        Sets the password for the specified user.

        This function is only applicable for users whose authentication method is `DEFAULT`.

        Args:
            user_id (str): The ID of the target user.
            password (str): The password for the target user.
            encrypted (bool): Whether the passed password is already encrypted.
                This value is false by default.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified user does not have an account
                type which supports a password.
            EncryptionException: If there was a problem handling the encryption for the password.
        """
        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        if not encrypted:
            password = Database.generate_encrypted_password(password)

        # pylint: disable=import-outside-toplevel
        # This import is valid
        from .models import Password

        try:
            with self.session_generator() as session:
                session.query(Password).filter_by(user_id=user_id).update(
                    {"phrase": password}
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def validate_password(self, user_id: str, password: str) -> bool:
        """
        Returns true if the provided unencrypted password matches the
        password stored in the database for the specified user.

        If the stored password needs to be rehashed, this function will
        rehash it and update it in the database.

        Args:
            user_id (str): The ID of the target user.
            password (str): The password for the target user.

        Returns:
            True if the the provided unencrypted password matches the password
            stored in the database for the specified user and false otherwise.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
            InvalidArgumentException: If the specified user does not have
                an account type which supports a password.
            EncryptionException: If there was a problem handling the encryption for the password.
        """
        hashed_password = self.get_user_password(user_id)

        hasher = PasswordHasher()
        try:
            hasher.verify(hashed_password, password)

            if hasher.check_needs_rehash(hashed_password):
                self.set_password(user_id, hasher.hash(password), encrypted=True)

            return True
        except (
            EncryptionException,
            NoUserException,
            InvalidArgumentException,
            DatabaseException,
        ) as exc:
            raise exc
        except (VerificationError, VerifyMismatchError, InvalidHash, HashingError):
            return False

    def set_profile_image(self, user_id: str, profile_image: str):
        """
        Sets the profile image URL for the specified user.

        Args:
            user_id (str): The ID of the target user.
            profile_image (str): The URL for the target user's profile image.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """
        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.query(User).filter_by(id=user_id).update(
                    {"profile_image": profile_image}
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def set_user_status(self, user_id: str, status: UserStatus):
        """
         Sets the status for the specified user.

        Args:
            user_id (str): The ID of the target user.
            status (UserStatus): The status of the target user.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """
        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.query(User).filter_by(id=user_id).update(
                    {"status": status.get_id()}
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def set_name(self, user_id: str, given_name: str, family_name: str):
        """
        Sets the name for the specified user.

        If you only want to set the given name and not the family
        name (or vice versa), set the one you don't want to change to
        `None` or use `set_given_name()` or `set_family_name()`.

        Args:
            user_id (str): The ID of the target user.
            given_name (str): The given name of the target user.
            family_name (str): The family name of the target user.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """
        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                user = session.query(User).filter_by(id=user_id)
                if given_name is not None:
                    user.update({"given_name": given_name})
                if family_name is not None:
                    user.update({"family_name": family_name})
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def set_given_name(self, user_id: str, given_name: str):
        """
        Sets the given name for the specified user.

        Args:
            user_id (str): The ID of the target user.
            given_name (str): The given name of the target user.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """
        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.query(User).filter_by(id=user_id).update(
                    {"given_name": given_name}
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def set_family_name(self, user_id: str, family_name: str):
        """
        Sets the family name for the specified user.

        Args:
            user_id (str): The ID of the target user.
            family_name (str): The family name of the target user.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """
        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.query(User).filter_by(id=user_id).update(
                    {"family_name": family_name}
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc

    def set_profile_visibility(self, user_id: str, profile_visibility: int):
        """
        Sets the profile visibility for the specified user.

        Args:
            user_id (str): The ID of the target user.
            profile_visibility (int): The profile visibility for the target user.

        Raises:
            DatabaseException: If there was a problem querying the database.
            NoUserException: If the specified user does not exist.
        """
        if not self.user_exists(user_id):
            raise NoUserException(user_id)

        # pylint: disable=import-outside-toplevel
        # This must be imported in this function
        from .models import User

        try:
            with self.session_generator() as session:
                session.query(User).filter_by(id=user_id).update(
                    {"profile_visibility": profile_visibility}
                )
                session.commit()
        except Exception as exc:
            raise DatabaseException("Failed to query database") from exc
