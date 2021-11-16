from flask import Blueprint, render_template
from flask_login import current_user
from flask_login.utils import login_required
import routes.util as util
from database.models import SavedRecipe, SavedIngredient
from api.spoonacular import get_recommended_recipes, SpoonacularApiException


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


@profile_blueprint.route("/profile")
@login_required
def profile():
    recipes = SavedRecipe.query.filter_by(user_id=current_user.id).all()
    ingredients = SavedIngredient.query.filter_by(user_id=current_user.id).all()
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
