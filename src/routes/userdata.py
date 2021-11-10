"""
==================== USERDATA ====================
This file defines all of the endpoints relating to user data, such as saving recipes and ingredients, deleting users, and more.
All of the endpoints defined in this file are API endpoints (i.e. they should not be navigated to using the browser's address bar).
"""

from flask import Blueprint, request, redirect, url_for
from flask.json import jsonify
from oauthlib.oauth2.rfc6749.clients.web_application import WebApplicationClient

from database.database import DuplicateUserException
from . import util
from flask_login import login_required, current_user, login_user, logout_user
from database.database import Database, DatabaseException
import os
import requests
import json

GOOGLE_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Used during the Google login flow
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
    return int__db.get_ingredient(id) != None


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
        The current user for the application, or `None` if there is no currently logged-in user.
    """
    return current_user


@userdata_blueprint.route("/api/save-recipe", methods=["POST"])
@login_required
def save_recipe():
    """
    Saves a recipe to the current user's list of saved recipes.
    If the recipe has not been cached in the server's global list of recipes, it is also stored there.

    This function does not validate the recipe data with Spoonacular.

    Parameters:
        id (int): The ID of the recipe.
        name (str): The display name of the recipe.
        image (str): The image URL of the recipe.

    Response:
        {
            result (int): The result of the operation, which is one of the following values:
                0: The recipe was saved successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem saving the recipe.
                3: There is no currently logged-in user (this error should never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_SAVE_FAIL = 2
    RESPONSE_ERR_NO_USER = 3

    id = request.args.get("id", type=int)
    name = request.args.get("name", type=str)
    image = request.args.get("image", type=str)

    if id == None or name == None or image == None:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()

    if user == None:
        return jsonify({"result": RESPONSE_ERR_NO_USER})

    if not recipe_exists(id):
        # Cache the recipe
        try:
            int__db.add_recipe(id, name, image)
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
    If the ingredient has not been cached in the server's global list of ingredients, it is also stored there.

    This function does not validate the ingredient data with Spoonacular.

    Parameters:
        id (int): The ID of the ingredient.
        name (str): The display name of the ingredient.
        image (str): The image URL of the ingredient.

    Response:
        {
            result (int): The result of the operation, which is one of the following values:
                0: The ingredient was saved successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem saving the ingredient.
                3: There is no currently logged-in user (this error should never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_SAVE_FAIL = 2
    RESPONSE_ERR_NO_USER = 3

    id = request.args.get("id", type=int)
    name = request.args.get("name", type=str)
    image = request.args.get("image", type=str)

    if id == None or name == None or image == None:
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
            result (int): The result of the operation, which is one of the following values:
                0: The recipe was deleted successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem deleting the recipe.
                3: There is no currently logged-in user (this error should never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_DELETE_FAIL = 2
    RESPONSE_ERR_NO_USER = 3

    id = request.args.get("id", type=int)

    if id == None:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()

    if user == None:
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
    Deletes the specified ingredient from the current user's list of saved ingredients.

    Parameters:
        id (int): The ID of the ingredient.

    Response:
        {
            result (int): The result of the operation, which is one of the following values:
                0: The ingredient was deleted successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem deleting the ingredient.
                3: There is no currently logged-in user (this error should never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_CORRUPT_INPUT = 1
    RESPONSE_ERR_DELETE_FAIL = 2
    RESPONSE_ERR_NO_USER = 3

    id = request.args.get("id", type=int)

    if id == None:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()

    if user == None:
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
            result (int): The result of the operation, which is one of the following values:
                0: The user was deleted successfully.
                1: There was a problem deleting the user.
                2: There is no currently logged-in user (this error should never occur, but it's listed here just in case).
        }
    """

    RESPONSE_OK = 0
    RESPONSE_ERR_DELETE_FAIL = 1
    RESPONSE_ERR_NO_USER = 2

    user = get_current_user()

    if user == None:
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
            result (int): The result of the operation, which is one of the following values:
                0: The username was updated successfully.
                1: The input arguments were corrupted or otherwise invalid.
                2: There was a problem updating the username.
                3: The specified username was already taken.
                4: There is no currently logged-in user (this error should never occur, but it's listed here just in case).
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

    if new_username == None:
        return jsonify({"result": RESPONSE_ERR_CORRUPT_INPUT})

    user = get_current_user()

    if user == None:
        return jsonify({"result": RESPONSE_ERR_NO_USER})

    try:
        int__db.set_username(user.id, new_username)
    except DuplicateUserException:
        return jsonify({"result": RESPONSE_ERR_DUP_UNAME})
    except DatabaseException:
        return jsonify({"result": RESPONSE_ERR_SET_UNAME_FAIL})

    return jsonify({"result": RESPONSE_OK})


@userdata_blueprint.route("/api/search-users", methods=["POST"])
@login_required
def search_users():
    """
    Searches the database for users which match the specified criteria.

    Parameters:
        criteria (str): The search criteria to use. This value must be one of the following:
            `given_name`: Search for users by their given name.
            `username`: Search for users by their username.
        query (str): The query string to use.
        offset (int): The offset into the search results to start at. This value is optional.
        limit (int): The maximum number of users to return. This value is optional.

    Response:
        {
            users (list): A list of user objects containing only their IDs, usernames, and given names.
        }

    If the search query failed, an empty JSON object will be returned and will not contain a `users` entry.
    """

    data = request.get_json()
    criteria = ""
    query = ""
    offset = 0
    limit = 10

    CRITERIA_GIVEN_NAME = "given_name"
    CRITERIA_USERNAME = "username"

    try:
        criteria = data["criteria"]
        query = data["query"]

        if (
            query == None
            or criteria == None
            or (criteria != CRITERIA_GIVEN_NAME and criteria != CRITERIA_USERNAME)
        ):
            return jsonify({})
    except KeyError:
        return jsonify({})

    try:
        offset = data["offset"]
        limit = data["limit"]
    except KeyError:
        pass

    users = []
    try:
        if criteria == CRITERIA_GIVEN_NAME:
            users = int__db.search_users_by_given_name(query, limit, offset)
        elif criteria == CRITERIA_USERNAME:
            users = int__db.search_users_by_username(query, limit, offset)
    except DatabaseException:
        return jsonify({})

    user_json = []
    for x in users:
        user_json.append({"id": x.id, "name": x.name, "username": x.username})

    return jsonify({"users": user_json})


# TODO: Fix this
@userdata_blueprint.route("/api2/start-login", methods=["POST"])
def start_login():
    """
    Initiates the login flow. The value returned by this function will be a redirect to Google's login handler URL.
    """
    google_provider = get_google_provider_cfg()
    authorization_endpoint = google_provider["authorization_endpoint"]
    dest_uri = request.url_root + "login/callback"
    request_uri = login_handler_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=dest_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


def validate_with_google(google_provider, code):
    """
    Ensures the code received by the /api/validate-login endpoint is valid and actually from Google.
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
    if response_json == None:
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
    if response_json == None:
        raise Exception("Invalid response")

    if not response_json.get("email_verified"):
        raise Exception("Email not verified with Google")

    user_id = response_json["sub"]
    user_email = response_json["email"]
    user_pfp = response_json["picture"]
    user_name = response_json["given_name"]
    return {"id": user_id, "email": user_email, "name": user_name, "image": user_pfp}


# TODO: Fix this
@userdata_blueprint.route("/login/callback")
def validate_login():
    """
    Validates that the attempted login was successful.

    Do not use this endpoint directly; it's only intended for use as a redirect destination from the Google login flow.
    """
    userinfo = None
    try:
        code = request.args.get("code")
        google_provider = get_google_provider_cfg()
        response = validate_with_google(google_provider, code)
        login_handler_client.parse_request_body_response(json.dumps(response))
        userinfo = get_google_user_info(google_provider)
    except Exception:
        return redirect("/login")

    user = int__db.get_user(userinfo["id"])

    if user == None:
        return redirect("/login")

    login_user(user)
    return redirect("/")


# TODO: Fix this
@userdata_blueprint.route("/api2/start-signup", methods=["POST"])
def start_signup():
    """
    Initiates the signup flow. The value returned by this function will be a redirect to Google's login handler URL.
    """
    google_provider = get_google_provider_cfg()
    authorization_endpoint = google_provider["authorization_endpoint"]
    dest_uri = request.url_root + "api/validate-signup/callback"
    request_uri = login_handler_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=dest_uri,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


# TODO: Fix this
@userdata_blueprint.route("/api2/validate-signup/callback")
def validate_signup():
    """
    Validates that the attempted signup was successful.

    Do not use this endpoint directly; it's only intended for use as a redirect destination from the Google login flow.
    """
    userinfo = None
    try:
        code = request.args.get("code")
        google_provider = get_google_provider_cfg()
        response = validate_with_google(google_provider, code)
        login_handler_client.parse_request_body_response(json.dumps(response))
        userinfo = get_google_user_info(google_provider)
    except Exception:
        return redirect("/signup")

    user = None
    try:
        user = int__db.add_user(
            userinfo["id"], userinfo["email"], userinfo["name"], userinfo["image"]
        )
    except DatabaseException:
        return redirect("/signup")

    login_user(user)
    return redirect("/")


# XXX: This is temporary
@userdata_blueprint.route("/api/start-login", methods=["POST"])
def start_login2():
    try:
        user = int__db.get_user("12345")
        if user == None:
            return redirect("/login")
        login_user(user)
    except DatabaseException:
        return redirect("/login")
    return redirect("/")


# XXX: This is temporary
@userdata_blueprint.route("/api/start-signup", methods=["POST"])
def start_signup2():
    try:
        user = int__db.add_user(
            "12345", "wgarland@piecemeal.com", name="William Garland"
        )
        login_user(user)
    except DatabaseException:
        return redirect("/signup")
    return redirect("/")
