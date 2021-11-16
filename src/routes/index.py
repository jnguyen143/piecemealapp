from flask import Blueprint, render_template
from flask_login import current_user

from api.spoonacular import SpoonacularApiException
from . import util
from flask_login import current_user
from api.spoonacular import get_recommended_recipes

index_blueprint = Blueprint(
    "bp_index",
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
    return index_blueprint


@index_blueprint.route("/")
def index():
    # If user is authenticated, get user recommendations based on saved ingredients and recipes
    if current_user.is_authenticated:
        return render_template("index2.html", userdata=current_user.to_json())
    # return render_template("index2.html", userdata=current_user.to_json())
    # Else, get dummy data/random recommendations
    recipes = []
    try:
        recipes = get_recommended_recipes()
    except SpoonacularApiException:
        pass

    return render_template("index.html", recipes=recipes, len=len(recipes))
