"""
This file contains miscellaneous API endpoints.
"""
import json
from os import getenv
from base64 import b64decode
from flask import Blueprint, request, Flask, redirect
from oauthlib.oauth2.rfc6749.clients.web_application import WebApplicationClient
import requests
from flask_login.utils import login_user
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256

from ...api.gmail import send_confirmation_email
from ...database.database import (
    Database,
    DatabaseException,
    DuplicateUserException,
    InvalidArgumentException,
    NoUserException,
    UserAuthentication,
)
from ... import util, keystore
from ..routing_util import (
    success_response,
    error_response,
    InvalidEndpointArgsException,
)


blueprint = Blueprint(
    "bp_api_misc",
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
GOOGLE_ID = None
GOOGLE_SECRET = None
GOOGLE_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Used during the Google login flow
login_handler_client = WebApplicationClient(GOOGLE_ID)


def init(app: Flask, database: Database):
    """
    Initializes this module.

    Args:
        app (Flask): The Flask application object.
        database (Database): The database object.
    """
    # pylint: disable=global-statement
    # We need to modify the global database and Google-related fields using this function
    global DATABASE
    global GOOGLE_ID
    global GOOGLE_SECRET

    DATABASE = database
    GOOGLE_ID = getenv("GOOGLE_CLIENT_ID")
    GOOGLE_SECRET = getenv("GOOGLE_CLIENT_SECRET")

    app.register_blueprint(get_blueprint())


@blueprint.route("/api/key/get")
def get_server_public_key():
    """
    Returns the server's public key used to encrypt certain requests made to the server.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            key (str): The server's public key.

        On failure, the possible error codes are:
            0 - A general exception occurred.
    """

    key = keystore.get_public_key()
    if key is None:
        return error_response(0, "Unknown error")
    return success_response({"key": key})


class InvalidResponseException(Exception):
    """
    Raised when an invalid response is received from an HTTP request.
    """

    def __init__(self):
        super().__init__("Invalid response")


def get_google_provider_cfg():
    """
    Returns the configuration for the Google login provider.

    Returns:
        The configuration JSON for the Google login flow.

    Raises:
        InvalidResponseException: If the response was invalid.
    """
    response = requests.get(GOOGLE_URL)
    if not response.ok:
        raise InvalidResponseException()
    json_value = response.json()
    if json_value is None:
        raise InvalidResponseException()
    return json_value


def login_default(data, error_responses):
    """
    Attempts to log in with default authentication using the provided input data.
    """

    try:
        username = util.get_or_raise(data, "username", InvalidEndpointArgsException())
        password = util.get_or_raise(data, "password", InvalidEndpointArgsException())
        user = DATABASE.get_user_by_username(username)

        if not DATABASE.validate_password(user.id, password):
            return error_response(3, error_responses[3])

        login_user(user)

        return success_response()
    except InvalidEndpointArgsException:
        return error_response(1, error_responses[1])
    except NoUserException:
        return error_response(3, error_responses[3])
    except InvalidArgumentException:
        return error_response(2, error_responses[2])
    except DatabaseException:
        return error_response(0, error_responses[0])


def login_google(error_responses):
    """
    Attempts to log in using Google authentication.
    """
    try:
        google_provider = get_google_provider_cfg()
        authorization_endpoint = google_provider["authorization_endpoint"]
        dest_uri = request.url_root + "api/validate-login/callback"
        request_uri = login_handler_client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=dest_uri,
            scope=["openid", "email", "profile"],
        )
        return success_response({"redirect_url": request_uri})
    # pylint: disable=broad-except
    # We don't want to pass any exceptions to the caller.
    except Exception:
        return error_response(0, error_responses[0])


@blueprint.route("/api/login/init", methods=["POST"])
def init_login():
    """
    Initiates the login flow.

    The arguments to this endpoint must be encrypted using the server's public key,
    which can be obtained using the `/api/key/get` endpoint.

    On success, the specified user will be logged in.

    Args:
        authentication (int): The authentication method to use.
        username (str): The target user's username.
            This value is only required if the authentication method is `DEFAULT` (0).
        password (str): The target user's password.
            This value is only required if the authentication method is `DEFAULT` (0).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            redirect_url (str): The redirect URL which should handle the external login.
                This value is only present if the authentication method is `GOOGLE` (1).

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
            2 - The provided authentication method is invalid.
            3 - The provided username or password is invalid.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
        "Invalid authentication method",
        "Invalid username or password",
    ]

    actual_data = None
    try:
        message = request.get_data()
        key = RSA.importKey(keystore.get_private_key())
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        decrypted_message = cipher.decrypt(b64decode(message))

        actual_data = json.loads(decrypted_message)
    # pylint: disable=broad-except
    # This block could yield any number of a wide range of exceptions.
    except Exception:
        return error_response(1, response_error_messages[1])

    authentication = UserAuthentication.DEFAULT
    try:
        authentication = UserAuthentication.get_from_value(
            util.get_or_raise(
                actual_data, "authentication", InvalidEndpointArgsException()
            )
        )
    except (InvalidEndpointArgsException, ValueError):
        return error_response(1, response_error_messages[1])

    if authentication == UserAuthentication.DEFAULT:
        return login_default(actual_data, response_error_messages)
    elif authentication == UserAuthentication.GOOGLE:
        return login_google(response_error_messages)
    else:
        return error_response(2, response_error_messages[2])


def signup_default(data, error_responses):
    """
    Attempts to sign up with default authentication using the provided input data.
    """

    try:
        username = util.get_or_raise(data, "username", InvalidEndpointArgsException())
        email = util.get_or_raise(data, "email", InvalidEndpointArgsException())
        password = util.get_or_raise(data, "password", InvalidEndpointArgsException())
        given_name = util.get_or_raise(
            data, "given_name", InvalidEndpointArgsException()
        )
        family_name = util.get_or_raise(
            data, "family_name", InvalidEndpointArgsException()
        )

        DATABASE.add_user(
            {
                "authentication": UserAuthentication.DEFAULT,
                "username": username,
                "email": email,
                "password": password,
                "given_name": given_name,
                "family_name": family_name,
            }
        )

        user = DATABASE.get_user_by_username(username)

        send_confirmation_email(email)

        login_user(user)

        return success_response()
    except InvalidEndpointArgsException:
        return error_response(1, error_responses[1])
    except DuplicateUserException:
        return error_response(4, error_responses[4])
    except InvalidArgumentException:
        return error_response(3, error_responses[3])
    except DatabaseException:
        return error_response(0, error_responses[0])


def signup_google(error_responses):
    """
    Attempts to sign up using Google authentication.
    """
    try:
        google_provider = get_google_provider_cfg()
        authorization_endpoint = google_provider["authorization_endpoint"]
        dest_uri = request.url_root + "api/validate-signup/callback"
        request_uri = login_handler_client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=dest_uri,
            scope=["openid", "email", "profile"],
        )
        return success_response({"redirect_url": request_uri})
    # pylint: disable=broad-except
    # We don't want to pass any exceptions to the caller.
    except Exception:
        return error_response(0, error_responses[0])


@blueprint.route("/api/signup/init", methods=["POST"])
def init_signup():
    """
    Initiates the signup flow.

    The arguments to this endpoint must be encrypted using the server's
    public key, which can be obtained using the `/api/key/get` endpoint.

    On success, the specified user will be logged in.

    Args:
        authentication (int): The authentication method to use.
        username (str): The target user's username.
            This value is only required if the authentication method is `DEFAULT` (0).
        email (str): The target user's email.
            This value is only required if the authentication method is `DEFAULT` (0).
        password (str): The target user's password.
            This value is only required if the authentication method is `DEFAULT` (0).
        given_name (str): The target user's given name.
            This value is only required if the authentication method is `DEFAULT` (0).
        family_name (str): The target user's family name.
            This value is only required if the authentication method is `DEFAULT` (0).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            redirect_url (str): The redirect URL which should handle the external login.
                This value is only present if the authentication method is `GOOGLE` (1).

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
            2 - The provided authentication method is invalid.
            3 - One or more of the provided fields has invalid syntax.
            4 - The specified username or email is already taken.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
        "Invalid authentication method",
        "Invalid syntax for input arguments",
    ]

    actual_data = None
    try:
        message = request.get_data()
        key = RSA.importKey(keystore.get_private_key())
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        decrypted_message = cipher.decrypt(b64decode(message))

        actual_data = json.loads(decrypted_message)
    # pylint: disable=broad-except
    # This block could yield any number of a wide range of exceptions.
    except Exception:
        return error_response(1, response_error_messages[1])

    authentication = UserAuthentication.DEFAULT
    try:
        authentication = UserAuthentication.get_from_value(
            util.get_or_raise(
                actual_data, "authentication", InvalidEndpointArgsException()
            )
        )
    except (InvalidEndpointArgsException, ValueError):
        return error_response(1, response_error_messages[1])

    if authentication == UserAuthentication.DEFAULT:
        return signup_default(actual_data, response_error_messages)
    elif authentication == UserAuthentication.GOOGLE:
        return signup_google(response_error_messages)
    else:
        return error_response(2, response_error_messages[2])


def validate_with_google(google_provider, code):
    """
    Ensures the code received by the `/api/validate-login/callback` endpoint is valid
    and actually from Google.
    """
    token_endpoint = google_provider["token_endpoint"]

    token_url, headers, body = login_handler_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )

    response = requests.post(
        token_url, headers=headers, data=body, auth=(GOOGLE_ID, GOOGLE_SECRET)
    )

    if not response.ok:
        raise InvalidResponseException()
    response_json = response.json()
    if response_json is None:
        raise InvalidResponseException()
    return response_json


def get_google_user_info(google_provider):
    """
    Returns the user information for the user associated with the client object.
    """
    userinfo_endpoint = google_provider["userinfo_endpoint"]
    uri, headers, body = login_handler_client.add_token(userinfo_endpoint)
    response = requests.get(uri, headers=headers, data=body)

    if not response.ok:
        raise InvalidResponseException()
    response_json = response.json()
    if response_json is None:
        raise InvalidResponseException()

    if not response_json.get("email_verified"):
        raise InvalidResponseException()

    user_id = response_json["sub"]
    user_email = response_json["email"]
    user_pfp = response_json["picture"]
    given_name = response_json["given_name"]
    family_name = response_json["family_name"]
    return {
        "id": user_id,
        "email": user_email,
        "given_name": given_name,
        "family_name": family_name,
        "profile_image": user_pfp,
    }


@blueprint.route("/api/validate-login/callback")
def validate_login_callback():
    """
    This route is for use only as a callback to a Google auth flow.
    """
    userinfo = None
    try:
        code = request.args.get("code")
        google_provider = get_google_provider_cfg()
        response = validate_with_google(google_provider, code)
        login_handler_client.parse_request_body_response(json.dumps(response))
        userinfo = get_google_user_info(google_provider)
    # pylint: disable=broad-except
    # We don't want to pass any exceptions to the caller.
    except Exception:
        return redirect("/login?login-auth-status=1")

    try:
        user = DATABASE.get_user_by_id(userinfo["id"])

        # With Google-authenticated accounts, Google controls the user's email and name.
        # Therefore they need to be updated to reflect Google's changes.
        if user.email != userinfo["email"]:
            DATABASE.set_email(user.id, userinfo["email"])
        DATABASE.set_name(user.id, userinfo["given_name"], userinfo["family_name"])

        login_user(user)
        return redirect("/")
    except DatabaseException:
        return redirect("/login?login-auth-status=2")


@blueprint.route("/api/validate-signup/callback")
def validate_signup_callback():
    """
    This route is for use only as a callback to a Google auth flow.
    """
    userinfo = None
    try:
        code = request.args.get("code")
        google_provider = get_google_provider_cfg()
        response = validate_with_google(google_provider, code)
        login_handler_client.parse_request_body_response(json.dumps(response))
        userinfo = get_google_user_info(google_provider)
    # pylint: disable=broad-except
    # We don't want to pass any exceptions to the caller.
    except Exception:
        return redirect("/signup?signup-auth-status=1")

    try:
        DATABASE.add_user(
            {
                "authentication": UserAuthentication.GOOGLE,
                "id": userinfo["id"],
                "email": userinfo["email"],
                "given_name": userinfo["given_name"],
                "family_name": userinfo["family_name"],
                "profile_image": userinfo["profile_image"],
            }
        )

        user = DATABASE.get_user_by_id(userinfo["id"])

        send_confirmation_email(userinfo["email"])

        login_user(user)

        return redirect("/")
    except DatabaseException:
        return redirect("/signup?signup-auth-status=2")
