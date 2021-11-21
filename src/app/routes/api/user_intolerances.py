"""
This file contains endpoints related to user intolerance data.
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
    "bp_api_user_intolerances",
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


def validate_intolerance_object(intolerance_obj: dict):
    """
    Checks the provided intolerance object to ensure it has all of the necessary fields.

    If any of the required fields are missing, this function will raise an exception.
    """
    util.get_or_raise(intolerance_obj, "id", InvalidEndpointArgsException())
    util.get_or_raise(intolerance_obj, "name", InvalidEndpointArgsException())


@blueprint.route("/api/user-intolerances/get")
@login_required
def get_user_intolerances():
    """
    Returns a list of intolerance objects which the current user has saved.

    Args:
        offset (int): The offset into the list to start at.
            This value must be greater than or equal to 0 and is optional (by default, it is 0).
        limit (int): The maximum number of intolerances to return.
            This value must be greater than or equal to 0 and is optional
            (by default, it is 0, which tells the server to return all of
            the current user's saved intolerances).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            intolerances: A list of Intolerance objects. This list will be empty if
                the user has no saved intolerances.
            total_intolerances (int): A value describing the total amount of
                intolerances the current user has.

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

        intolerances = DATABASE.get_intolerances(user_id, offset, limit)
        return success_response(
            {
                "intolerances": [
                    intolerance.to_json() for intolerance in intolerances[0]
                ],
                "total_intolerances": intolerances[1],
            }
        )
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-intolerances/add", methods=["POST"])
@login_required
def add_user_intolerance():
    """
    Adds the specified intolerance to the current user's list of saved intolerances.

    Args:
        intolerance: The intolerance to save, which must be an Intolerance object.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The user already has the specified intolerance.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "Duplicate intolerance entry",
    ]

    try:
        data = get_json_data(request)
        intolerance = util.get_or_raise(
            data, "intolerance", InvalidEndpointArgsException()
        )

        validate_intolerance_object(intolerance)

        user_id = get_current_user().id

        result = DATABASE.add_intolerance(user_id, intolerance)

        if not result:
            return error_response(3, response_error_messages[3])
        return success_response()
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(2, response_error_messages[2])
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-intolerances/delete", methods=["POST"])
@login_required
def delete_user_intolerance():
    """
    Deletes the specified intolerance from the current user's list of saved intolerances.

    Args:
        id (int): The ID of the intolerance to delete.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The user does not have the specified intolerance.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "No intolerance entry exists for the current user with the specified ID",
    ]

    try:
        data = get_json_data(request)
        intolerance_id = util.get_or_raise(data, "id", InvalidEndpointArgsException())

        user_id = get_current_user().id

        result = DATABASE.delete_intolerance(user_id, intolerance_id)

        if not result:
            return error_response(3, response_error_messages[3])

        return success_response()
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(2, response_error_messages[2])
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])
