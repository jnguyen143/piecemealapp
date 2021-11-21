"""
This file contains user-facing endpoints relating to index pages.
"""
import random
from flask import Flask, Blueprint, render_template
from ...database.database2 import (
    Database,
)
from ... import util
from ..routing_util import NoCurrentUserException, get_current_user
from ...api import spoonacular

blueprint = Blueprint(
    "bp_direct_index",
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


@blueprint.route("/")
def index():
    """
    Returns the index page.
    """

    try:
        current_user = get_current_user()
        return user_index_page(current_user)
    except NoCurrentUserException:
        return general_index_page()


def get_recommended_recipes_from_spoonacular():
    """
    Returns recommended recipes from Spoonacular.

    This function is necessary for some unit tests.
    """
    return spoonacular.get_recommended_recipes()


def get_similar_recipes_from_spoonacular(recipe_id):
    """
    Returns similar recipes from Spoonacular.

    This function is necessary for some unit tests.
    """
    return spoonacular.get_similar_recipes(recipe_id)


def user_index_page(current_user):
    """
    The index page for when a user is logged in.
    """
    target_recipes = []

    (recipes, _) = DATABASE.get_recipes(current_user.id)
    if len(recipes) > 0:
        # Select one of the recipes from user's profile randomly
        recipe_sample = random.choice(recipes)
        # recipe_sample = recipe_sample.recipe_id
        # Get similar recipes based on selected sample
        try:
            target_recipes = get_similar_recipes_from_spoonacular(recipe_sample)
        except spoonacular.SpoonacularApiException:
            pass
    else:
        try:
            target_recipes = get_recommended_recipes_from_spoonacular()
        except spoonacular.SpoonacularApiException:
            pass

    return render_template(
        "index2.html",
        recipes=target_recipes,
        has_recipes=len(target_recipes) > 0,
        userdata=current_user.to_json(),
    )


def general_index_page():
    """
    The index page for when no user is logged in.
    """
    recipes = []
    try:
        recipes = get_recommended_recipes_from_spoonacular()
    except spoonacular.SpoonacularApiException:
        pass

    return render_template("index.html", recipes=recipes, len=len(recipes))