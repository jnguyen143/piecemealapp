"""
This file contains endpoints related to users.
"""
from flask import Blueprint, request, Flask
from ...database.database import (
    Database,
    DatabaseException,
    InvalidArgumentException,
    NoUserException,
)
from ... import util
from ..routing_util import (
    get_json_data,
    success_response,
    error_response,
    InvalidEndpointArgsException,
)

blueprint = Blueprint(
    "bp_api_users",
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


@blueprint.route("/api/users/search")
def search_users():
    """
    Returns a list of users which match the specified query string.

    Note that when attempting to search by full name, given name, or family name,
    if a user's name is not publicly visible, they will not show up in the search results.

    Args:
        query (str): The query string to use.
        search_by (str): The field to search by. This must be one of:
            username: The user's username.
            full_name: The user's given and family name.
            given_name: The user's given name.
            family_name: The user's family name.
        offset (int): The offset into the search results to start at.
            This value must be greater than or equal to 0 and is optional (by default, it is 0).
        limit (int): The maximum number of users to return.
            This value must be greater than or equal to 0 and is optional (by default, it is 10).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            results: A list of User objects representing the search results.
            total_results (int): A value describing the total amount of search
                results for the given query.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
    ]

    try:
        data = get_json_data(request)
        query = util.get_or_raise(data, "query", InvalidEndpointArgsException())
        search_by = util.get_or_raise(data, "search_by", InvalidEndpointArgsException())
        offset = util.get_or_default(data, "offset", 0)
        limit = util.get_or_default(data, "limit", 10)

        results = None

        if search_by == "username":
            results = DATABASE.search_users_by_username(query, offset, limit)
        elif search_by in ("full_name", "given_name", "family_name"):
            results = DATABASE.search_users_by_name(query, offset, limit)
        else:
            return error_response(1, response_error_messages[1])

        return success_response(
            {
                "results": [result.to_json(shallow=True) for result in results[0]],
                "total_results": results[1],
            }
        )
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/users/get")
def get_user():
    """
    Returns information describing the specified user.

    Args:
        query (str): The query to use.
        by (str): The field by which the user should be retrieved. This must be one of:
            id: Get a user by their ID.
            username: Get a user by their username.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            user: A User object.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
            2 - No user exists which matches the provided query.
            3 - The specified `by` condition is invalid.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
    ]

    try:
        data = get_json_data(request)
        query = util.get_or_raise(data, "query", InvalidEndpointArgsException())
        get_by = util.get_or_raise(data, "by", InvalidEndpointArgsException())

        result = None
        if get_by == "id":
            result = DATABASE.get_user_by_id(query)
        elif get_by == "username":
            result = DATABASE.get_user_by_username(query)
        else:
            return error_response(3, response_error_messages[3])

        return success_response({"user": result.to_json(shallow=True)})
    except InvalidEndpointArgsException:
        return error_response(1, response_error_messages[1])
    except NoUserException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])
