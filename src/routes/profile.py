from flask import Blueprint, render_template
from flask_login import current_user
from flask_login.utils import login_required
import routes.util as util
from database.models import SavedRecipe
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
    ingredients = []
    print("Recipes are: ", recipes)
    if recipes:
        return render_template(
            "profile.html",
            recipes=recipes,
            len=len(recipes),
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
            len=len(recipes),
            userdata=current_user.to_json(),
        )
