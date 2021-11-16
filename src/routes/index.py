from flask import Blueprint, render_template
from flask_login import current_user

from api.spoonacular import SpoonacularApiException
from . import util
from flask_login import current_user
from api.spoonacular import get_recommended_recipes
from database.models import SavedRecipe

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
        recipes = []
        saved_recipes = SavedRecipe.query.filter_by(user_id=current_user.id).all()
        if saved_recipes:
            print("Saved recipes are: ", saved_recipes)
            print("What is to json: ", current_user.to_json())
            return render_template(
                "index.html",
                recipes=recipes,
                len=len(recipes),
                userdata=current_user.to_json(),
            )
        else:
            try:
                recipes = get_recommended_recipes()
            except SpoonacularApiException:
                pass

            return render_template(
                "index2.html",
                recipes=recipes,
                len=len(recipes),
                userdata=current_user.to_json(),
            )

    # Else, get dummy data/random recommendations
    recipes = []
    try:
        recipes = get_recommended_recipes()
    except SpoonacularApiException:
        pass

    return render_template("index.html", recipes=recipes, len=len(recipes))
