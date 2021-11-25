"""
This file contains user-facing endpoints relating to profile pages.
"""
from flask import Flask, Blueprint, render_template
from flask_login import login_required
from ...database.database import (
    Database,
)
from ... import util
from ..routing_util import get_current_user
from ...api import spoonacular

blueprint = Blueprint(
    "bp_direct_profile",
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


@blueprint.route("/profile")
@login_required
def profile():
    """
    Returns the profile page.
    """
    current_user = get_current_user()
    (recipes, _) = DATABASE.get_recipes(current_user.id)
    (ingredients, _) = DATABASE.get_ingredients(current_user.id)

    if len(recipes) == 0:
        try:
            recipes = spoonacular.get_recommended_recipes()
        except spoonacular.SpoonacularApiException:
            pass

    return render_template(
        "profile.html",
        recipes=[recipe.to_json() for recipe in recipes],
        has_recipes=len(recipes) > 0,
        ingredients=[ingredient.to_json() for ingredient in ingredients],
        has_ingredient=len(ingredients) > 0,
        userdata=current_user.to_json(shallow=True),
    )
