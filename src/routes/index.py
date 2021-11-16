from flask import Blueprint, render_template
from flask_login import current_user
<<<<<<< Updated upstream
from random import sample, choice
from api.spoonacular import SpoonacularApiException
from . import util
from flask_login import current_user
from api.spoonacular import get_recommended_recipes, get_similar_recipes
from database.models import SavedRecipe
=======

from . import util
from api.spoonacular import (
    SpoonacularApiException,
    get_recommended_recipes,
    get_similar_recipes,
)
from database import database
from random import choice

>>>>>>> Stashed changes

index_blueprint = Blueprint(
    "bp_index",
    __name__,
    template_folder=util.get_templates_folder(),
    static_folder=util.get_static_folder(),
)

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


def get_blueprint():
    """
    Returns the `Blueprint` object which stores all of the functions in this file.

    All routing files have the same function to retrieve their blueprints.

    Returns:
        The blueprint object for this file.
    """
    return index_blueprint


<<<<<<< Updated upstream
=======
def get_current_user():
    """
    Returns the current user for the application.

    Returns:
        The current user for the application, or `None` if there is no currently logged-in user.
    """
    return current_user


def get_recommended_recipes_from_spoonacular():
    return get_recommended_recipes()


def get_similar_recipes_from_spoonacular(recipe_id):
    return get_similar_recipes(recipe_id)


def is_user_authenticated():
    return current_user and current_user.is_authenticated


>>>>>>> Stashed changes
@index_blueprint.route("/")
def index():
    recipes = []
    # If user is authenticated, get user recommendations based on saved ingredients and recipes
<<<<<<< Updated upstream
    if current_user.is_authenticated:
        print("The user passed authentication")
        saved_recipes = SavedRecipe.query.filter_by(user_id=current_user.id).all()
=======
    if is_user_authenticated():
        print("The user passed authentication")
        saved_recipes = int__db.get_saved_recipes(get_current_user().id)

>>>>>>> Stashed changes
        if saved_recipes:
            # Select one of the recipes from user's profile randomly
            recipe_sample = choice(saved_recipes)
            recipe_sample = recipe_sample.recipe_id
            # Get similar recipes based on selected sample
            try:
<<<<<<< Updated upstream
                recipes = get_similar_recipes(recipe_sample)
=======
                recipes = get_similar_recipes_from_spoonacular(recipe_sample)

>>>>>>> Stashed changes
            except SpoonacularApiException:
                pass

            return render_template(
                "index2.html",
                recipes=recipes,
                len=len(recipes),
                has_recipes=True,
                userdata=current_user.to_json(),
            )
        # If user has no recipes saved, display randomly recommended recipes for user to add
        else:
            try:
<<<<<<< Updated upstream
                recipes = get_recommended_recipes()
=======
                recipes = get_recommended_recipes_from_spoonacular()

>>>>>>> Stashed changes
            except SpoonacularApiException:
                pass

            return render_template(
                "index2.html",
                recipes=recipes,
                len=len(recipes),
                userdata=current_user.to_json(),
            )

    # Else if user not authorized, get dummy data/random recommendations
    print("The user sucks")
    try:
<<<<<<< Updated upstream
        recipes = get_recommended_recipes()
=======
        recipes = get_recommended_recipes_from_spoonacular()
>>>>>>> Stashed changes
    except SpoonacularApiException:
        pass

    return render_template("index.html", recipes=recipes, len=len(recipes))
