"""
==================== USERDATA ====================
This file defines all of the endpoints relating to user data, such as saving recipes and
ingredients, deleting users, and more. All of the endpoints defined in this file are API
endpoints (i.e. they should not be navigated to using the browser's address bar).
"""
import os
import json
import dotenv
from flask import Blueprint, request, redirect
from flask.json import jsonify
import requests
from oauthlib.oauth2.rfc6749.clients.web_application import WebApplicationClient
from flask_login import login_required, current_user, login_user, logout_user

# pylint: disable=import-error
# This import is valid
from database.database import (
    DuplicateUserException,
    UserAuthentication,
    DatabaseException,
    Database,
    NoUserException,
)
import keystore as keystore
from . import util

dotenv.load_dotenv(dotenv.find_dotenv())

GOOGLE_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Used during the Google login flow
# pylint: disable=C0103
login_handler_client = WebApplicationClient(GOOGLE_ID)

userdata_blueprint = Blueprint(
    "bp_userdata",
    __name__,
    template_folder=util.get_templates_folder(),
    static_folder=util.get_static_folder(),
)


def get_blueprint():
    """
    Returns the `Blueprint` object which stores all of the functions in this file.

    All routing files have the same function to retrieve their blueprints.

    Returns:
        The blueprint object for this file.
    """
    return userdata_blueprint


# For internal use only
int__db: Database = None


def recipe_exists(id):
    return int__db.get_recipe(id) != None


def ingredient_exists(id):
    # pylint: disable=C0103
    return int__db.get_ingredient(id) != None


# pylint: disable=C0103
def init(db: Database):
    """
    Initializes this module using the provided arguments.

    Args:
        db (Database): The database object to use.
    """
    global int__db
    int__db = db


def get_current_user():
    """
    Returns the current user for the application.

    Returns:
        The current user for the application, or `None` if there is no currently
        logged-in user.
    """
    return current_user


@userdata_blueprint.route("/api/save-recipe", methods=["POST"])
@login_required
def save_recipe():
    """
    Saves a recipe to the current user's list of saved recipes.
    If the recipe has not been cached in the server's global list of recipes,
    it is also stored there.

    This function does not validate the recipe data with Spoonacular.

    Parameters:
        id (int): The ID of the recipe.
        name (str): The display name of the recipe.
        image (str): The image URL of the recipe.

    Response:
        {
            result (int): The result of the operation, which is one of the
            following values:
                0: The recipe was saved successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem saving the recipe.
                3: There is no currently logged-in user (this error should
                never occur, but it's listed here just in case).
        }
    """
    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_SAVE_FAIL = 2
    RESPONSE_ERR_NO_USER = 3

    id = None
    name = None
    image = None

    try:
        data = request.get_json()
        id = data["id"]
        name = data["name"]
        image = data["image"]
        summary = data["summary"]
        full_summary = data["full_summary"]
    except KeyError:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()
    if user is None:
        return jsonify({"result": RESPONSE_ERR_NO_USER})
    if not recipe_exists(id):
        # Cache the recipe
        try:
            int__db.add_recipe(id, name, image, summary, full_summary)
        except DatabaseException:
            return jsonify({"result": RESPONSE_ERR_SAVE_FAIL})
    try:
        int__db.add_saved_recipe(user.id, id)
    except DatabaseException:
        return jsonify({"result": RESPONSE_ERR_SAVE_FAIL})
    return jsonify({"result": RESPONSE_OK})


@userdata_blueprint.route("/api/save-ingredient", methods=["POST"])
@login_required
def save_ingredient():
    """
    Saves a ingredient to the current user's list of saved ingredients.
    If the ingredient has not been cached in the server's global list of
    ingredients, it is also stored there.

    This function does not validate the ingredient data with Spoonacular.

    Parameters:
        id (int): The ID of the ingredient.
        name (str): The display name of the ingredient.
        image (str): The image URL of the ingredient.

    Response:
        {
            result (int): The result of the operation, which is one of the
            following values:
                0: The ingredient was saved successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem saving the ingredient.
                3: There is no currently logged-in user (this error should
                never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_SAVE_FAIL = 2
    RESPONSE_ERR_NO_USER = 3

    id = None
    name = None
    image = None

    try:
        data = request.get_json()
        id = data["id"]
        name = data["name"]
        image = data["image"]
    except KeyError:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()
    if user == None:
        return jsonify({"result": RESPONSE_ERR_NO_USER})

    if not ingredient_exists(id):
        # Cache the ingredient
        try:
            int__db.add_ingredient(id, name, image)
        except DatabaseException:
            return jsonify({"result": RESPONSE_ERR_SAVE_FAIL})
    try:
        int__db.add_saved_ingredient(user.id, id)
    except DatabaseException:
        return jsonify({"result": RESPONSE_ERR_SAVE_FAIL})
    return jsonify({"result": RESPONSE_OK})


@userdata_blueprint.route("/api/delete-recipe", methods=["POST"])
@login_required
def delete_recipe():
    """
    Deletes the specified recipe from the current user's list of saved recipes.

    Parameters:
        id (int): The ID of the recipe.

    Response:
        {
            result (int): The result of the operation, which is one of the
            following values:
                0: The recipe was deleted successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem deleting the recipe.
                3: There is no currently logged-in user (this error should
                never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_DELETE_FAIL = 2
    RESPONSE_ERR_NO_USER = 3

    try:
        data = request.get_json()
        id = data["id"]
    except KeyError:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    if id == None:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()

    if user is None:
        return jsonify({"result": RESPONSE_ERR_NO_USER})

    try:
        int__db.delete_saved_recipe(user.id, id)
    except DatabaseException:
        return jsonify({"result": RESPONSE_ERR_DELETE_FAIL})

    return jsonify({"result": RESPONSE_OK})


@userdata_blueprint.route("/api/delete-ingredient", methods=["POST"])
@login_required
def delete_ingredient():
    """
    Deletes the specified ingredient from the current user's list of saved
    ingredients.

    Parameters:
        id (int): The ID of the ingredient.

    Response:
        {
            result (int): The result of the operation, which is one of the
            following values:
                0: The ingredient was deleted successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem deleting the ingredient.
                3: There is no currently logged-in user (this error should
                never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_DELETE_FAIL = 2
    RESPONSE_ERR_NO_USER = 3

    try:
        data = request.get_json()
        id = data["id"]
    except KeyError:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    if id is None:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()

    if user is None:
        return jsonify({"result": RESPONSE_ERR_NO_USER})

    try:
        int__db.delete_saved_ingredient(user.id, id)
    except DatabaseException:
        return jsonify({"result": RESPONSE_ERR_DELETE_FAIL})

    return jsonify({"result": RESPONSE_OK})


def get_google_provider_cfg():
    """
    Returns the configuration for the Google login provider.

    Returns:
        The configuration JSON for the Google login flow.

    Raises:
        Exception: If the response was invalid.
    """
    response = requests.get(GOOGLE_URL)
    if not response.ok:
        raise Exception("Invalid response")
    json_value = response.json()
    if json_value == None:
        raise Exception("Invalid response")
    return json_value


@userdata_blueprint.route("/api/delete-user", methods=["POST"])
@login_required
def delete_user():
    """
    Deletes the current user and forces a logout.

    Response:
        {
            result (int): The result of the operation, which is one
            of the following values:
                0: The user was deleted successfully.
                1: There was a problem deleting the user.
                2: There is no currently logged-in user (this error
                should never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_DELETE_FAIL = 1
    RESPONSE_ERR_NO_USER = 2

    user = get_current_user()

    if user is None:
        return jsonify({"result": RESPONSE_ERR_NO_USER})

    try:
        int__db.delete_user(user.id)
    except DatabaseException:
        return jsonify({"result": RESPONSE_ERR_DELETE_FAIL})

    logout_user()

    return jsonify({"result": RESPONSE_OK})


@userdata_blueprint.route("/api/update-username", methods=["POST"])
@login_required
def update_username():
    """
    Sets the current user's username to the specified username.

    Parameters:
        new_username (str): The new username to use.

    Response:
        {
            result (int): The result of the operation, which is one
            of the following values:
                0: The username was updated successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem updating the username.
                3: The specified username was already taken.
                4: There is no currently logged-in user (this error should
                never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_SET_UNAME_FAIL = 2
    RESPONSE_ERR_DUP_UNAME = 3
    RESPONSE_ERR_NO_USER = 4

    new_username = None

    try:
        new_username = request.get_json()["new_username"]
    except KeyError:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    if new_username is None:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()

    if user is None:
        return jsonify({"result": RESPONSE_ERR_NO_USER})

    try:
        int__db.set_username(user.id, new_username)
    except DuplicateUserException:
        return jsonify({"result": RESPONSE_ERR_DUP_UNAME})
    except DatabaseException:
        return jsonify({"result": RESPONSE_ERR_SET_UNAME_FAIL})

    return jsonify({"result": RESPONSE_OK})


def dict_get_or_default(dict, key, default):
    try:
        return dict[key]
    except KeyError:
        return default


@userdata_blueprint.route("/api/search-users", methods=["POST"])
@login_required
def search_users():
    """
    Searches the database for users which match the specified criteria.

    Parameters:
        criteria (str): The search criteria to use. This value must
        be one of the following:
            `name`: Search for users by their name.
            `username`: Search for users by their username.
        query (str): The query string to use.
        offset (int): The offset into the search results to start at.
        This value is optional.
        limit (int): The maximum number of users to return. This value
        is optional.
        exclude_current (bool): Whether the search should exclude the
        currently logged-in user. This value is optional and is true by default.

    Response:
        {
            users (list): A list of user objects containing only their
            IDs, usernames, and names.
        }

    If the search query failed, an empty JSON object will be returned and
    will not contain a `users` entry.
    """

    data = request.get_json()
    criteria = ""
    query = ""

    CRITERIA_NAME = "name"
    CRITERIA_USERNAME = "username"

    try:
        criteria = data["criteria"]
        query = data["query"]

        if (
            query is None
            or criteria is None
            or (criteria != CRITERIA_NAME, CRITERIA_USERNAME)
        ):
            return jsonify({})
    except KeyError:
        return jsonify({})

    offset = dict_get_or_default(data, "offset", 0)
    limit = dict_get_or_default(data, "limit", 10)
    exclude_current = dict_get_or_default(data, "exclude_current", True)

    users = []
    try:
        if criteria == CRITERIA_NAME:
            users = int__db.search_users_by_name(query, limit, offset)
        elif criteria == CRITERIA_USERNAME:
            users = int__db.search_users_by_username(query, limit, offset)
    except DatabaseException:
        return jsonify({})

    user_json = []
    for x in users:
        if exclude_current and x.id == current_user.id:
            continue
        user_json.append(
            {
                "id": x.id,
                "given_name": x.given_name,
                "family_name": x.family_name,
                "username": x.username,
            }
        )

    return jsonify({"users": user_json})


@userdata_blueprint.route("/api/start-login", methods=["POST"])
def start_login():
    """
    Initiates the login flow. The value returned by this function will be
    a redirect to Google's login handler URL.

    The input data for this endpoint must be encrypted using the correct public key.

    Parameters:
        authentication (str): The authentication method to use. This value
        should be one of the values in `database.UserAuthentication`.
        username (str): The user's username. This value is optional depending
        on the authentication method.
        password (str): The user's password. This value is optional depending
        on the authentication method.

    Response:
        If the authentication method is `database.UserAuthentication.Google`,
        then this function will return a redirect to Google's login handler URL.

        Otherwise, the following value will be returned:
        {
            success (bool): Whether the user was successfully logged in.
        }
    """

    message = ""
    try:
        message = request.get_data()
    except:
        print("test1")
        return jsonify({"success": False})

    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    from base64 import b64decode

    decrypted_message = ""
    try:
        key = RSA.importKey(keystore.get_private_key())
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        decrypted_message = cipher.decrypt(b64decode(message))
    except:
        print("test2")
        return jsonify({"success": False})

    actual_data = json.loads(decrypted_message)

    auth = dict_get_or_default(actual_data, "authentication", None)
    if auth == UserAuthentication.Google.label:
        google_provider = get_google_provider_cfg()
        authorization_endpoint = google_provider["authorization_endpoint"]
        dest_uri = request.url_root + "api/validate-login/callback"
        request_uri = login_handler_client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=dest_uri,
            scope=["openid", "email", "profile"],
        )
        return jsonify({"redirect_url": request_uri, "success": True})
    elif auth == UserAuthentication.Default.label:
        try:
            username = actual_data["username"]
            password = actual_data["password"]
            user = int__db.get_user_by_username(username)
            if int__db.validate_password(user.id, password):
                login_user(user)
                return jsonify({"success": True})
            else:
                print("test3")
                return jsonify({"success": False})
        except Exception as E:
            print(E)
            print("test4")
            return jsonify({"success": False})
    else:
        print("test5")
        return jsonify({"success": False})


def validate_with_google(google_provider, code):
    """
    Ensures the code received by the /api/validate-login endpoint is valid
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
        raise Exception("Invalid response")
    response_json = response.json()
    if response_json is None:
        raise Exception("Invalid response")
    return response_json


def get_google_user_info(google_provider):
    """
    Returns the user information for the user associated with the client object.
    """
    userinfo_endpoint = google_provider["userinfo_endpoint"]
    uri, headers, body = login_handler_client.add_token(userinfo_endpoint)
    response = requests.get(uri, headers=headers, data=body)

    if not response.ok:
        raise Exception("Invalid response")
    response_json = response.json()
    if response_json is None:
        raise Exception("Invalid response")

    if not response_json.get("email_verified"):
        raise Exception("Email not verified with Google")

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
        "image": user_pfp,
    }


@userdata_blueprint.route("/api/validate-login/callback")
def validate_login():
    """
    Validates that the attempted login was successful.

    If there was a problem logging in using the Google account, this function
    will redirect back to the `/login` endpoint with an error flag set in the
    request parameters.

    Do not use this endpoint directly; it's only intended for use as a redirect
    destination from the Google login flow.
    """
    userinfo = None
    try:
        code = request.args.get("code")
        google_provider = get_google_provider_cfg()
        response = validate_with_google(google_provider, code)
        login_handler_client.parse_request_body_response(json.dumps(response))
        userinfo = get_google_user_info(google_provider)
    except Exception:
        return redirect("/login?login-auth-status=1")

    user = int__db.get_user(userinfo["id"])

    if user is None:
        return redirect("/login?login-auth-status=2")

    # With Google-authenticated accounts, Google controls the user's email and name. Therefore they need to be updated to reflect Google's changes
    int__db.set_userdata(
        user.id,
        email=userinfo["email"],
        given_name=userinfo["given_name"],
        family_name=userinfo["family_name"],
    )

    login_user(user)
    return redirect("/")


@userdata_blueprint.route("/api/start-signup", methods=["POST"])
def start_signup():
    """
    Initiates the signup flow. The value returned by this function will be
    a JSON object containing information about the result of the call.

    The input data for this endpoint must be encrypted using the correct public key.

    Parameters:
        authentication (str): The authentication method to use. This value should
        be one of the values in `database.UserAuthentication`.
        username (str): The user's username. This value is optional depending on
        the authentication method.
        email (str): The user's email. This value is optional depending on the
        authentication method.
        given_name (str): The user's given name. This value is optional depending
        on the authentication method.
        family_name (str): The user's family name. This value is optional depending
        on the authentication method.
        password (str): The user's password. This value is optional depending
        on the authentication method.

    Response:
        {
            success (bool): Whether the user was successfully created and logged in.
            redirect_url (str): The destination URL for a Google-authenticated
            signup request. This value is only present if the authentication method
            is `database.UserAuthentication.Google`.
        }
    """
    message = ""
    try:
        message = request.get_data()
    except:
        return jsonify({"success": False})

    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    from base64 import b64decode

    decrypted_message = ""
    try:
        key = RSA.importKey(keystore.get_private_key())
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        decrypted_message = cipher.decrypt(b64decode(message))
    except:
        return jsonify({"success": False})

    actual_data = json.loads(decrypted_message)

    auth = dict_get_or_default(actual_data, "authentication", None)
    if auth == UserAuthentication.Google.label:
        google_provider = get_google_provider_cfg()
        authorization_endpoint = google_provider["authorization_endpoint"]
        dest_uri = request.url_root + "api/validate-signup/callback"
        request_uri = login_handler_client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=dest_uri,
            scope=["openid", "email", "profile"],
        )
        return {"redirect_url": str(request_uri), "success": True}
    elif auth == UserAuthentication.Default.label:
        try:
            username = actual_data["username"]
            email = actual_data["email"]
            given_name = actual_data["given_name"]
            family_name = actual_data["family_name"]
            password = actual_data["password"]
            user = int__db.add_default_user(
                email, password, username, given_name, family_name
            )
            login_user(user)
            return jsonify({"success": True})
        except:
            return jsonify({"success": False})
    else:
        return jsonify({"success": False})


@userdata_blueprint.route("/api/validate-signup/callback")
def validate_signup():
    """
    Validates that the attempted signup was successful.

    Do not use this endpoint directly; it's only intended for use as a redirect
    destination from the Google login flow.
    """
    userinfo = None
    try:
        code = request.args.get("code")
        google_provider = get_google_provider_cfg()
        response = validate_with_google(google_provider, code)
        login_handler_client.parse_request_body_response(json.dumps(response))
        userinfo = get_google_user_info(google_provider)
    except Exception as E:
        print("Error1", E)
        return redirect("/signup")

    user = None
    try:
        user = int__db.add_google_user(
            userinfo["id"],
            userinfo["email"],
            given_name=userinfo["given_name"],
            family_name=userinfo["family_name"],
            profile_image=userinfo["image"],
        )
    except DatabaseException as E:
        print("Error2", E)
        return redirect("/signup")

    login_user(user)
    return redirect("/")


@userdata_blueprint.route("/api/get-public-key")
def get_server_public_key():
    """
    Returns the server's public key for use in encrypting data that should be
    sent back to the server.

    Response:
    {
        key (str): The server's public key (as a string).
    }
    """
    return jsonify({"key": keystore.get_public_key()})


@userdata_blueprint.route("/api/update-password", methods=["POST"])
def update_password():
    """
    Updates the current user's password.

    The input data for this endpoint must be encrypted using the correct public
    key.

    Parameters:
        old_password (str): The user's current password.
        new_password (str): The new password to use.

    Response:
        {
            result (int): The result of the operation, which is one of the following values:
                0: The password was updated successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: The old password was incorrect.
                3: The user's account type does not allow for passwords.
                4: There was a problem updating the username.
                5: There is no currently logged-in user (this error should never
                occur, but it's listed here just in case).
        }
    """
    RESPONSE_OK = 0
    RESPONSE_CORRUPT_INPUT = 1
    RESPONSE_INVALID_PASSWORD = 2
    RESPONSE_INVALID_AUTH = 3
    RESPONSE_PASSWORD_SET_FAIL = 4
    RESPONSE_NO_USER = 5

    message = ""
    try:
        message = request.get_data()
    except:
        return jsonify({"result": RESPONSE_CORRUPT_INPUT})

    from Crypto.Cipher import PKCS1_OAEP
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    from base64 import b64decode

    decrypted_message = ""
    try:
        key = RSA.importKey(keystore.get_private_key())
        cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256)
        decrypted_message = cipher.decrypt(b64decode(message))
    except:
        return jsonify({"result": RESPONSE_CORRUPT_INPUT})

    actual_data = json.loads(decrypted_message)
    old_ps = ""
    new_ps = ""

    try:
        old_ps = actual_data["old_password"]
        new_ps = actual_data["new_password"]
    except KeyError:
        return jsonify({"result": RESPONSE_CORRUPT_INPUT})

    user = get_current_user()

    if user is None:
        return jsonify({"result": RESPONSE_NO_USER})

    try:
        if not int__db.validate_password(user.id, old_ps):
            return jsonify({"result": RESPONSE_INVALID_PASSWORD})
    except NoUserException:
        return jsonify({"result": RESPONSE_INVALID_AUTH})
    except:
        return jsonify({"result": RESPONSE_PASSWORD_SET_FAIL})

    try:
        int__db.set_password(user.id, new_ps)
    except:
        return jsonify({"result": RESPONSE_PASSWORD_SET_FAIL})

    return jsonify({"result": RESPONSE_OK})


@userdata_blueprint.route("/api/delete-relationship", methods=["POST"])
def delete_friend():
    """
    Deletes the relationship between the current user and the specified user.

    This operation works both ways; the relationship will be deleted for the
    current user against the specified user and vice versa.

    Parameters:
        user_id (str): The ID of the related user to be deleted.

    Response:
        {
            result (int): The result of the operation, which is one of the following values:
                0: The relationship was deleted successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: The current user does not have a relationship with the specified user.
                3: There was a problem deleting the relationship.
                4: There is no currently logged-in user (this error should
                never occur, but it's listed here just in case).
        }
    """
    RESPONSE_OK = 0
    RESPONSE_CORRUPT_INPUT = 1
    RESPONSE_NO_RELATIONSHIP = 2
    RESPONSE_RELATIONSHIP_DELETE_FAIL = 3
    RESPONSE_NO_USER = 4

    user_id = None

    try:
        user_id = request.get_json()["user_id"]
    except KeyError:
        return jsonify({"result": RESPONSE_CORRUPT_INPUT})

    user = get_current_user()

    if user is None:
        return jsonify({"result": RESPONSE_NO_USER})

    try:
        int__db.delete_relationship(user.id, user_id)
    except NoUserException:
        return jsonify({"result": RESPONSE_NO_RELATIONSHIP})
    except:
        return jsonify({"result": RESPONSE_RELATIONSHIP_DELETE_FAIL})

    return jsonify({"result": RESPONSE_OK})


@userdata_blueprint.route("/api/send-friend-request", methods=["POST"])
def send_friend_request():
    """
    Sends a friend request from the current user to the specified user.

    Parameters:
        user_id (str): The ID of the user to receive the request.

    Response:
        {
            result (int): The result of the operation, which is one of the
            following values:
                0: The request was sent successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: The specified user does not exist.
                3: There was a problem sending the request.
                4: There is no currently logged-in user (this error should
                never occur, but it's listed here just in case).
        }
    """
    RESPONSE_OK = 0
    RESPONSE_CORRUPT_INPUT = 1
    RESPONSE_NO_TARGET_USER = 2
    RESPONSE_REQUEST_ADD_FAIL = 3
    RESPONSE_NO_USER = 4

    user_id = None

    try:
        user_id = request.get_json()["user_id"]
    except KeyError:
        return jsonify({"result": RESPONSE_CORRUPT_INPUT})

    user = get_current_user()

    if user is None:
        return jsonify({"result": RESPONSE_NO_USER})

    try:
        int__db.add_friend_request(user.id, user_id)
    except NoUserException:
        return jsonify({"result": RESPONSE_NO_TARGET_USER})
    except:
        return jsonify({"result": RESPONSE_REQUEST_ADD_FAIL})

    return jsonify({"result": RESPONSE_OK})


@userdata_blueprint.route("/api/handle-friend-request", methods=["POST"])
def handle_friend_request():
    """
    Handles the friend request for the current user against the specified user.

    If the friend request is accepted, this function will delete the request
    from the table and add a relationship between the current user and the specified user.

    Parameters:
        user_id (str): The ID of the user who sent the request.
        action (int): The action to perform on the request, which must be one of:
            0: Deny the request.
            1: Accept the request.

    Response:
        {
            result (int): The result of the operation, which is one of the
            following values:
                0: The action was performed successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: The specified user does not exist.
                3: There was a problem performing the action.
                4: There is no currently logged-in user (this error should
                never occur, but it's listed here just in case).
        }
    """
    RESPONSE_OK = 0
    RESPONSE_CORRUPT_INPUT = 1
    RESPONSE_NO_SRC_USER = 2
    RESPONSE_REQUEST_ACTION_FAIL = 3
    RESPONSE_NO_USER = 4

    ACTION_DENY = 0
    ACTION_ACCEPT = 1

    user_id = None
    action = None

    try:
        data = request.get_json()
        user_id = data["user_id"]
        action = int(data["action"])
    except KeyError:
        return jsonify({"result": RESPONSE_CORRUPT_INPUT})

    user = get_current_user()

    if user is None:
        return jsonify({"result": RESPONSE_NO_USER})

    if action == ACTION_ACCEPT:
        try:
            int__db.delete_friend_request(user_id, user.id)
            int__db.add_relationship(user.id, user_id)
        except NoUserException:
            print("err1")
            return jsonify({"result": RESPONSE_NO_SRC_USER})
        except Exception as exception:
            print(f"err2: {exception}")
            return jsonify({"result": RESPONSE_REQUEST_ACTION_FAIL})
    elif action == ACTION_DENY:
        try:
            result = int__db.delete_friend_request(user_id, user.id)
            if not result:
                return jsonify({"result": RESPONSE_REQUEST_ACTION_FAIL})
        except NoUserException:
            return jsonify({"result": RESPONSE_NO_SRC_USER})
        except:
            return jsonify({"result": RESPONSE_REQUEST_ACTION_FAIL})
    else:
        return jsonify({"result": RESPONSE_CORRUPT_INPUT})

    return jsonify({"result": RESPONSE_OK})