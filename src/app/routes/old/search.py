from flask import Blueprint, render_template, request
from flask_login import current_user
from werkzeug.datastructures import ImmutableHeadersMixin

# pylint: disable=import-error
# This import is valid
import routes.util as util

# pylint: disable=import-error
# This import is valid
from api.spoonacular import Cuisine, search_recipes, search_ingredients


search_blueprint = Blueprint(
    "bp_search",
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
    return search_blueprint


# Route that searches ingredients the user can add to profile
@search_blueprint.route("/search_ingredients", methods=["POST"])
def searchByingredients():
    if request.method == "POST":
        ingredients = request.form.get("searchIngredients")
        keyword = ingredients
        # pylint: disable=C0103
        returnedDict = search_ingredients(ingredients)
        if returnedDict == []:
            print("No ingredients produced by API call")
        return render_template(
            "index2.html" if current_user.is_authenticated else "index.html",
            ingredients=returnedDict,
            keyword=keyword,
            search=True,
            userdata=current_user.to_json() if current_user.is_authenticated else None,
        )
    return render_template("index.html")


# Route that searches for recipes based on user input keyword
@search_blueprint.route("/search_recipes", methods=["POST"])
# pylint: disable=C0103
def searchByrecipes():
    if request.method == "POST":
        keyword = request.form.get("searchRecipes")
        cuisine = request.form.get("cuisine")
        query_string = keyword + ", " + cuisine
        # pylint: disable=C0103
        returnedDict = search_recipes(query_string)
        if returnedDict == []:
            print("No recipes produced by API call")
        return render_template(
            "index2.html" if current_user.is_authenticated else "index.html",
            recipes=returnedDict,
            keyword=keyword,
            search=True,
            recipe_search=True,
            userdata=current_user.to_json() if current_user.is_authenticated else None,
        )
    return render_template("index.html")
