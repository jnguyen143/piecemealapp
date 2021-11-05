"""
==================== USERDATA ====================
This file defines all of the endpoints relating to user data, such as saving recipes and ingredients, deleting users, and more.
All of the endpoints defined in this file are API endpoints (i.e. they should not be navigated to using the browser's address bar).
"""

from flask import Blueprint, request
from flask.json import jsonify
import util as util
from flask_login import login_required
from database.database import Database, DatabaseException

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


def set_db_obj(db: Database):
    """
    Sets this module's stored database object to the provided object.

    Args:
        db (Database): The database object to use.
    """
    global int__db
    int__db = db


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

    # TODO: Force a logout

    return jsonify({"result": RESPONSE_OK})
