"""
This file contains endpoints related to user ingredient data.
"""
from flask import Blueprint, request, Flask
from flask_login import login_required
from ...database.database2 import (
    Database,
    DatabaseException,
    InvalidArgumentException,
)
from ... import util
from ..routing_util import (
    get_json_data,
    success_response,
    error_response,
    get_current_user,
    InvalidEndpointArgsException,
    NoCurrentUserException,
)

blueprint = Blueprint(
    "bp_api_user_ingredients",
    __name__,
    template_folder=util.get_templates_folder(),
    static_folder=util.get_static_folder(),
)


def get_blueprint() -> Blueprint:
    """
    Returns the `Blueprint` object which stores all of the functions in this file.

    All routing files have the same function to retrieve their blueprints.

    Returns:
        The blueprint object for this file.
    """
    return blueprint


DATABASE: Database = None


def init(app: Flask, database: Database):
    """
    Initializes this module.

    Args:
        app (Flask): The Flask application object.
        database (Database): The database object.
    """
    # pylint: disable=global-statement
    # We need to modify the global database object using this function
    global DATABASE

    DATABASE = database

    app.register_blueprint(get_blueprint())


def validate_ingredient_object(ingredient_obj: dict):
    """
    Checks the provided ingredient object to ensure it has all of the necessary fields.

    If any of the required fields are missing, this function will raise an exception.
    """
    util.get_or_raise(ingredient_obj, "id", InvalidEndpointArgsException())
    util.get_or_raise(ingredient_obj, "name", InvalidEndpointArgsException())
    util.get_or_raise(ingredient_obj, "image", InvalidEndpointArgsException())


@blueprint.route("/api/user-ingredients/get")
@login_required
def get_user_ingredients():
    """
    Returns a list of ingredient objects which the current user has saved.

    Args:
        offset (int): The offset into the list to start at.
            This value must be greater than or equal to 0 and is optional (by default, it is 0).
        limit (int): The maximum number of ingredients to return.
            This value must be greater than or equal to 0 and is optional
            (by default, it is 0, which tells the server to return all of
            the current user's ingredients).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            ingredients: A list of Ingredient objects. This list will be empty if
                the user has no saved ingredients.
            total_ingredients (int): A value describing the total amount of
                ingredients the current user has.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
    ]

    data = None
    try:
        data = get_json_data(request)
    except InvalidEndpointArgsException:
        pass  # If no data was passed, that's okay; all of the fields are optional.

    offset = 0
    limit = 0

    if data is not None:
        offset = util.get_or_default(data, "offset", 0)
        limit = util.get_or_default(data, "limit", 0)

    try:
        user_id = get_current_user().id

        ingredients = DATABASE.get_ingredients(user_id, offset, limit)
        return success_response(
            {
                "ingredients": [ingredient.to_json() for ingredient in ingredients[0]],
                "total_ingredients": ingredients[1],
            }
        )
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-ingredients/add", methods=["POST"])
@login_required
def add_user_ingredient():
    """
    Adds the specified ingredient to the current user's list of saved ingredients.

    Args:
        ingredient: The ingredient to save, which must be an Ingredient object.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The user already has the specified ingredient.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "Duplicate ingredient entry",
    ]

    try:
        data = get_json_data(request)
        ingredient = util.get_or_raise(
            data, "ingredient", InvalidEndpointArgsException()
        )

        validate_ingredient_object(ingredient)

        user_id = get_current_user().id

        result = DATABASE.add_ingredient(user_id, ingredient)

        if not result:
            return error_response(3, response_error_messages[3])
        return success_response()
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(2, response_error_messages[2])
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-ingredients/delete", methods=["POST"])
@login_required
def delete_user_ingredient():
    """
    Deletes the specified ingredient from the current user's list of saved ingredients.

    Args:
        id (int): The ID of the ingredient to delete.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The user does not have the specified ingredient.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "No ingredient entry exists for the current user with the specified ID",
    ]

    try:
        data = get_json_data(request)
        ingredient_id = util.get_or_raise(data, "id", InvalidEndpointArgsException())

        user_id = get_current_user().id

        result = DATABASE.delete_ingredient(user_id, ingredient_id)

        if result:
            return success_response()
        else:
            return error_response(3, response_error_messages[3])
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(2, response_error_messages[2])
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-ingredients/get-top")
@login_required
def get_user_top_ingredients():
    """
    Returns a list of a random selection from the current user's most recently liked ingredients.

    The algorithm will look at only the most recently liked ingredients and will only retrieve
    up to the specified limit of ingredients.

    Args:
        limit (int): The maximum number of ingredients to return.
            This value must be greater than or equal to 0 and is optional
            (by default, the limit is 5).

    Returns:
    On success, a JSON object containing the following fields:
        success (bool): Whether the request was successfully completed.
        ingredients: A list of Ingredient objects. This list is guaranteed to
            be less than or equal to the specified limit.

    On failure, the possible error codes are:
        0 - A general exception occurred.
        1 - There is no user currently logged in.
        2 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
    ]

    data = None
    try:
        data = get_json_data(request)
    except InvalidEndpointArgsException:
        pass

    limit = 5
    if data is not None:
        limit = util.get_or_default(data, "limit", 5)

    try:
        user_id = get_current_user().id

        ingredients = DATABASE.get_user_top_ingredients(user_id, limit)

        return success_response(
            {"ingredients": [ingredient.to_json() for ingredient in ingredients]}
        )
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-ingredients/get-friend-top")
@login_required
def get_friend_top_ingredients():
    """
    Returns a list of user/ingredient list pairs generated based off of the liked ingredients
    of the current user's friends.

    The algorithm will look at only the most recently liked ingredients and will only retrieve
    up to the specified limit of ingredients per friend.

    Args:
        friend_limit (int): The maximum amount of friends to sample from.
            This value must be greater than or equal to 0 and is optional
            (by default, the limit is 5).
        limit_per_friend (int): The maximum amount of ingredients to retrieve
            per friend. This value must be greater than or equal to 0 and
            is optional (by default, the limit is 5).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            friends: A list of objects containing the following fields:
                friend: A User object describing the associated friend.
                ingredients: A list of Ingredient objects representing the friend's top ingredients.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
    ]

    data = None
    try:
        data = get_json_data(request)
    except InvalidEndpointArgsException:
        pass

    friend_limit = 5
    limit_per_friend = 5
    if data is not None:
        friend_limit = util.get_or_default(data, "friend_limit", 5)
        limit_per_friend = util.get_or_default(data, "limit_per_friend", 5)

    try:
        user_id = get_current_user().id

        friends = DATABASE.get_friend_top_ingredients(
            user_id, friend_limit, limit_per_friend
        )

        result = []

        for friend in friends:
            result.append(
                {
                    "friend": friend["user"].to_json(shallow=True),
                    "ingredients": [
                        ingredient.to_json() for ingredient in friend["ingredients"]
                    ],
                }
            )

        return success_response({"friends": result})
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])
