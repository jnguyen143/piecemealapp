"""
This file contains endpoints related to global recipe data.
"""
from flask import Blueprint, request, Flask
from ...database.database2 import Database, DatabaseException, NoRecipeException
from ... import util
from ..routing_util import (
    get_post_json,
    success_response,
    error_response,
    InvalidEndpointArgsException,
)

blueprint = Blueprint(
    "bp_api_global_recipes",
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


@blueprint.route("/api/recipe-info/get")
def get_recipe_info():
    """
    Returns a JSON object containing the recipe information
    for the recipe with the specified ID.

    Args:
        id (int): The ID of the target recipe.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            recipe: A Recipe object.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
            2 - No recipe exists with the provided ID.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
        "No recipe exists with the provided ID",
    ]

    recipe_id = None
    try:
        data = get_post_json(request)
        recipe_id = util.get_or_raise(data, "id", InvalidEndpointArgsException())
    except InvalidEndpointArgsException:
        return error_response(1, response_error_messages[1])

    try:
        recipe = DATABASE.get_recipe_info(recipe_id)
        return success_response(recipe.to_json())
    except NoRecipeException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])
