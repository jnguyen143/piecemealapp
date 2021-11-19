from flask import Blueprint, render_template
from flask_login import current_user
from flask_login.utils import login_required

# pylint: disable=import-error
# This import is valid
import routes.util as util

# pylint: disable=import-error
# This import is valid
from api.spoonacular import get_recommended_recipes, SpoonacularApiException

# pylint: disable=import-error
# This import is valid
from database import database


profile_blueprint = Blueprint(
    "bp_profile",
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
    return profile_blueprint


# For internal use only
int__db: database.Database = None


def init(db: database.Database):
    """
    Initializes this module using the provided arguments.

    Args:
        db (Database): The database object to use.
    """
    global int__db
    int__db = db


@profile_blueprint.route("/profile")
@login_required
def profile():
    recipes = [
        recipe.to_json() for recipe in int__db.get_saved_recipes(current_user.id)
    ]
    ingredients = [
        ingredient.to_json()
        for ingredient in int__db.get_saved_ingredients(current_user.id)
    ]
    has_recipes = False
    has_ingredients = False

    # If user has recipes, set has to true
    if recipes:
        has_recipes = True
    # If user has no recipes saved, display randomly recommended recipes for user to add
    else:
        try:
            recipes = get_recommended_recipes()
        except SpoonacularApiException:
            pass

    # if user has ingredients, set has to true
    if ingredients:
        has_ingredients = True

    return render_template(
        "profile.html",
        recipes=recipes,
        ingredients=ingredients,
        has_recipes=has_recipes,
        has_ingredients=has_ingredients,
        userdata=current_user.to_json(),
    )
