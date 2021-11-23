"""
This file contains endpoints related to user account information.
"""
import json
from base64 import b64decode
from flask import Blueprint, request, Flask
from flask_login.utils import logout_user
from flask_login import login_required
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from ...database.database import (
    Database,
    DatabaseException,
    DuplicateUserException,
    InvalidArgumentException,
)
from ... import util, keystore
from ..routing_util import (
    get_json_data,
    success_response,
    error_response,
    get_current_user,
    InvalidEndpointArgsException,
    NoCurrentUserException,
)

blueprint = Blueprint(
    "bp_api_account",
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


def revert_user(original_data: dict):
    """
    Reverts the specified user to their original data.
    """
    try:
        DATABASE.set_email(original_data["id"], original_data["email"])
    except DatabaseException:
        pass
    try:
        DATABASE.set_username(original_data["id"], original_data["username"])
    except DatabaseException:
        pass
    try:
        DATABASE.set_name(
            original_data["id"],
            original_data["given_name"],
            original_data["family_name"],
        )
    except DatabaseException:
        pass
    try:
        DATABASE.set_profile_image(original_data["id"], original_data["profile_image"])
    except DatabaseException:
        pass


class AccountInfoSetException(Exception):
    """
    Represents an error which is raised if there is a problem modifying account info.
    """

    def __init__(self, error_code):
        super().__init__()
        self.error_code = error_code


def try_set_email(data, user_id):
    """
    Tries to set the email for the specified user.
    """
    error_code = -1

    try:
        email = util.get_or_raise(data, "email", InvalidEndpointArgsException())
        DATABASE.set_email(user_id, email)
    except InvalidEndpointArgsException:
        pass  # If it's not present, that's fine; it's optional.
    except InvalidArgumentException:
        error_code = 2
    except DuplicateUserException:
        error_code = 3
    except DatabaseException:
        error_code = 0

    if error_code != -1:
        raise AccountInfoSetException(error_code)


def try_set_username(data, user_id):
    """
    Tries to set the username for the specified user.
    """
    error_code = -1

    try:
        username = util.get_or_raise(data, "username", InvalidEndpointArgsException())
        DATABASE.set_username(user_id, username)
    except InvalidEndpointArgsException:
        pass  # If it's not present, that's fine; it's optional.
    except InvalidArgumentException:
        error_code = 2
    except DuplicateUserException:
        error_code = 3
    except DatabaseException:
        error_code = 0

    if error_code != -1:
        raise AccountInfoSetException(error_code)


def try_set_given_name(data, user_id):
    """
    Tries to set the given name for the specified user.
    """
    error_code = -1

    try:
        given_name = util.get_or_raise(
            data, "given_name", InvalidEndpointArgsException()
        )
        DATABASE.set_given_name(user_id, given_name)
    except InvalidEndpointArgsException:
        pass  # If it's not present, that's fine; it's optional.
    except DatabaseException:
        error_code = 0

    if error_code != -1:
        raise AccountInfoSetException(error_code)


def try_set_family_name(data, user_id):
    """
    Tries to set the family name for the specified user.
    """
    error_code = -1

    try:
        family_name = util.get_or_raise(
            data, "family_name", InvalidEndpointArgsException()
        )
        DATABASE.set_family_name(user_id, family_name)
    except InvalidEndpointArgsException:
        pass  # If it's not present, that's fine; it's optional.
    except DatabaseException:
        error_code = 0

    if error_code != -1:
        raise AccountInfoSetException(error_code)


def try_set_profile_image(data, user_id):
    """
    Tries to set the given name for the specified user.
    """
    error_code = -1

    try:
        profile_image = util.get_or_raise(
            data, "profile_image", InvalidEndpointArgsException()
        )
        DATABASE.set_profile_image(user_id, profile_image)
    except InvalidEndpointArgsException:
        pass  # If it's not present, that's fine; it's optional.
    except DatabaseException:
        error_code = 0

    if error_code != -1:
        raise AccountInfoSetException(error_code)


@blueprint.route("/api/account/update", methods=["POST"])
@login_required
def update_account():
    """
    Updates the current user's account according to the provided information.

    All arguments to this endpoint are optional.

    Args:
        email (str): The user's email.
        username (str): The user's username.
        given_name (str): The user's given name.
        family_name (str): The user's family name.
        profile_image (str): The user's profile image.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - One or more of the input arguments contain invalid syntax.
            3 - The specified email and/or username was already taken.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Invalid syntax in input arguments",
        "Email and/or username already taken",
    ]

    user_id = None
    try:
        user_id = get_current_user().id
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])

    data = None
    try:
        data = get_json_data(request)
    except InvalidEndpointArgsException:
        # If no data was passed, that's okay; all of the fields are optional.
        return success_response()

    original_data = None
    try:
        # Get the original user data in case any of the input fields
        # were corrupted so we can revert.
        original_data = DATABASE.get_user_by_id(user_id).to_json(shallow=True)
    except DatabaseException:
        return error_response(0, response_error_messages[0])

    try:
        try_set_email(data, user_id)
        try_set_username(data, user_id)
        try_set_given_name(data, user_id)
        try_set_family_name(data, user_id)
        try_set_profile_image(data, user_id)
    except AccountInfoSetException as exc:
        revert_user(original_data)
        return error_response(exc.error_code, response_error_messages[exc.error_code])

    return success_response()


@blueprint.route("/api/account/update-password", methods=["POST"])
@login_required
def update_password():
    """
    Updates the current user's password.

    This endpoint only applies to users whose authentication method is
    `DEFAULT` (i.e. users who have an account directly through PieceMeal).

    The arguments to this endpoint must be encrypted using the server's public key,
    which can be obtained using the `/api/key/get` endpoint.

    Args:
        old_password (str): The user's current password.
        new_password (str): The new password to use.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The old password was invalid.
    """
    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "Invalid current password",
    ]

    old_password = ""
    new_password = ""
    try:
        message = request.get_data()
        key = RSA.importKey(keystore.get_private_key())
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        decrypted_message = cipher.decrypt(b64decode(message))

        actual_data = json.loads(decrypted_message)
        old_password = actual_data["old_password"]
        new_password = actual_data["new_password"]
    # pylint: disable=broad-except
    # This block could yield any number of a wide range of exceptions.
    except Exception:
        return error_response(2, response_error_messages[2])

    try:
        user_id = get_current_user().id

        if not DATABASE.validate_password(user_id, old_password):
            return error_response(3, response_error_messages[3])

        DATABASE.set_password(user_id, new_password)

        return success_response()
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/account/delete", methods=["POST"])
@login_required
def delete_account():
    """
    Deletes the current user's account and invalidates the session.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
    ]

    try:
        user_id = get_current_user().id
        logout_user()
        DATABASE.delete_user(user_id)
        return success_response()
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])
