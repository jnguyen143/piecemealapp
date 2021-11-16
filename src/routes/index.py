from flask import Blueprint, render_template
from flask_login import current_user
from random import choice
from . import util
from flask_login import current_user
from api.spoonacular import (
    get_recommended_recipes,
    get_similar_recipes,
    SpoonacularApiException,
)
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
    recipes = []
    # If user is authenticated, get user recommendations based on saved ingredients and recipes
    if current_user.is_authenticated:
        saved_recipes = SavedRecipe.query.filter_by(user_id=current_user.id).all()
        if saved_recipes:
            # Select one of the recipes from user's profile randomly
            recipe_sample = choice(saved_recipes)
            recipe_sample = recipe_sample.recipe_id
            # Get similar recipes based on selected sample
            try:
                recipes = get_similar_recipes(recipe_sample)
            except SpoonacularApiException:
                pass

            return render_template(
                "index2.html",
                recipes=recipes,
                has_recipes=True,
                userdata=current_user.to_json(),
            )
        # If user has no recipes saved, display randomly recommended recipes for user to add
        else:
            try:
                recipes = get_recommended_recipes()
            except SpoonacularApiException:
                pass

            return render_template(
                "index2.html",
                recipes=recipes,
                userdata=current_user.to_json(),
            )

    # Else if user not authorized, get dummy data/random recommendations
    try:
        recipes = get_recommended_recipes()
    except SpoonacularApiException:
        pass

    return render_template("index.html", recipes=recipes, len=len(recipes))
