"""
This file contains endpoints related to user friends.
"""
from flask import Blueprint, request, Flask
from flask_login import login_required
from ...database.database2 import (
    Database,
    DatabaseException,
    InvalidArgumentException,
    NoUserException,
)
from ... import util
from ..routing_util import (
    NoCurrentUserException,
    get_current_user,
    get_json_data,
    success_response,
    error_response,
    InvalidEndpointArgsException,
)

blueprint = Blueprint(
    "bp_api_friends",
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


@blueprint.route("/api/friends/get")
@login_required
def get_friends():
    """
    Returns a list of the current user's friends.

    Args:
        offset (int): The offset into the list to start at.
            This value must be greater than or equal to 0 and is optional (by default, it is 0).
        limit (int): The maximum number of friends to return.
            This value must be greater than or equal to 0 and is optional
            (by default, it is 0, which tells the server to return
            all of the current user's friends).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            friends: A list of User objects representing the current user's friends.
            total_friends (int): A value describing the total amount of
                friends the current user has.

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

    offset = 0
    limit = 0
    if data is not None:
        offset = util.get_or_default(data, "offset", 0)
        limit = util.get_or_default(data, "limit", 0)

    try:
        user_id = get_current_user().id

        friends = DATABASE.get_relationships_for_user(user_id, offset, limit)

        return success_response(
            {
                "friends": [friend.to_json(shallow=True) for friend in friends[0]],
                "total_friends": friends[1],
            }
        )
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/friends/send-request", methods=["POST"])
@login_required
def send_friend_request():
    """
    Sends a friend request from the current user to the target user.

    Args:
        target (str): The ID of the user to receive the request.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The user has already sent the request.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "Request has already been sent",
    ]

    try:
        data = get_json_data(request)
        target = util.get_or_raise(data, "target", InvalidEndpointArgsException())

        user_id = get_current_user().id

        result = DATABASE.add_friend_request(user_id, target)

        if not result:
            return error_response(3, response_error_messages[3])
        return success_response()
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(2, response_error_messages[2])
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/friends/handle-request", methods=["POST"])
@login_required
def handle_friend_request():
    """
    Processes the request for the current user and the specified source user.

    Args:
        src (str): The ID of the user who sent the request.
        action (int): The action to perform, which must be one of:
            0 - Deny the request. If this action is performed,
                the friend request will be deleted automatically.
            1 - Accept the request. If this action is performed,
                a relationship between the two users will be added
                and the friend request will be deleted.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The user has no friend request from the specified source user.
            4 - The specified source user does not exist.
            5 - The specified action is invalid.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "Friend request does not exist",
        "Source user does not exist",
        "Invalid action",
    ]

    try:
        data = get_json_data(request)
        src = util.get_or_raise(data, "src", InvalidEndpointArgsException())
        action = util.get_or_raise(data, "action", InvalidEndpointArgsException())

        user_id = get_current_user().id

        result = False
        if action == 0:
            # Deny the request
            result = DATABASE.delete_friend_request(src, user_id)
        elif action == 1:
            # Accept the request
            result = DATABASE.delete_friend_request(src, user_id)
            if result:
                DATABASE.add_relationship(src, user_id)
        else:
            return error_response(5, response_error_messages[5])

        if not result:
            return error_response(3, response_error_messages[3])
        return success_response()
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(2, response_error_messages[2])
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except NoUserException:
        return error_response(4, response_error_messages[4])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/friends/get-sent-requests")
@login_required
def get_sent_requests():
    """
    Returns a list of users that have received friend requests from the current user.

    Args:
        offset (int): The offset into the list to start at.
            This value must be greater than or equal to 0 and is optional (by default, it is 0).
        limit (int): The maximum number of users to return.
            This value must be greater than or equal to 0 and is optional (by default, it is 0,
            which tells the server to return all of the sent requests).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            targets: A list of User objects representing the users which have received
                friend requests from the current user.
            total_sent (int): A value describing the total amount of friend requests
                the current user has sent.

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

    offset = 0
    limit = 0
    if data is not None:
        offset = util.get_or_default(data, "offset", 0)
        limit = util.get_or_default(data, "limit", 0)

    try:
        user_id = get_current_user().id

        requests = DATABASE.get_friend_requests_for_source(user_id, offset, limit)

        return success_response(
            {
                "targets": [user.to_json(shallow=True) for user in requests[0]],
                "total_sent": requests[1],
            }
        )
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/friends/get-received-requests")
@login_required
def get_received_requests():
    """
    Returns a list of users that have sent friend requests to the current user.

    Args:
        offset (int): The offset into the list to start at.
            This value must be greater than or equal to 0 and is optional (by default, it is 0).
        limit (int): The maximum number of users to return.
            This value must be greater than or equal to 0 and is optional (by default, it is 0,
            which tells the server to return all of the received requests).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            sources: A list of User objects representing the users which
                have sent friend requests to the current user.
            total_received (int): A value describing the total amount of
                friend requests the current user has received.

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

    offset = 0
    limit = 0
    if data is not None:
        offset = util.get_or_default(data, "offset", 0)
        limit = util.get_or_default(data, "limit", 0)

    try:
        user_id = get_current_user().id

        requests = DATABASE.get_friend_requests_for_target(user_id, offset, limit)

        return success_response(
            {
                "sources": [user.to_json(shallow=True) for user in requests[0]],
                "total_received": requests[1],
            }
        )
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])
