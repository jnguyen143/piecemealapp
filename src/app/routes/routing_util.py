"""
This file defines utility functions specific to routes.
"""
from flask import jsonify
from flask_login import current_user


class InvalidEndpointArgsException(Exception):
    """
    Raised when an argument to an endpoint is invalid.
    """

    def __init__(self, arg: str = None):
        if arg is None:
            super().__init__("Invalid arguments sent to endpoint")
        else:
            super().__init__(f"Invalid argument sent to endpoint: {arg}")


class NoCurrentUserException(Exception):
    """
    Raised when there is no currently logged in user.
    """

    def __init__(self):
        super().__init__("No user is currently logged in")


def get_json_data(request, request_type: str = "GET") -> dict:
    """
    Returns a JSON object representing the data in the provided request.

    If `request_type` is `GET`, this function will look in the URL query arguments for data.
    If `request_type` is `POST`, this function will look in the request body for data.
    Otherwise, an exception will be raised.

    If the request does not have JSON data, this function raises an exception.
    """

    try:
        data: dict = None
        if request_type == "GET":
            data = request.args.to_dict()
        elif request_type == "POST":
            data = request.get_json()
        else:
            raise InvalidEndpointArgsException("Invalid request type")
        if data is None:
            raise InvalidEndpointArgsException("Expected JSON data")
        return data
    except InvalidEndpointArgsException as exc:
        raise exc
    except Exception as exc:
        raise InvalidEndpointArgsException() from exc


def error_response(code: int, message: str):
    """
    Creates a JSON error response containing the provided error information.
    """
    return jsonify({"success": False, "error_code": code, "error_message": message})


def success_response(data: dict = None):
    """
    Creates a JSON success response containing the provided data.
    """
    result = {"success": True}
    if data is not None:
        for key in data.keys():
            result[key] = data[key]
    return jsonify(result)


def get_current_user():
    """
    Returns the currently logged in user, or raises an exception if there is no user.
    """

    # pylint: disable=singleton-comparison
    # We have to also use the regular equality operator check
    # because apparently Werkzeug implements it weird
    if (
        current_user is not None
        and current_user != None
        and current_user.is_authenticated
    ):
        return current_user

    raise NoCurrentUserException()
