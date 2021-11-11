from flask import Blueprint, render_template, request
import routes.util as util
from api.spoonacular import search_recipes, search_ingredients

# import spoonacular functions search_recipes, search_ingredients

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



@search_blueprint.route("/search_ingredients", methods=["POST"])
def searchByingredients():
    if request.method == "POST":
        ingredients = request.form.get("searchIngredients")
        # prints what the user searches for to the terminal
        print(ingredients)
        returnedDict = search_ingredients(ingredients)
        # prints the 10 recipes to the terminal
        print(returnedDict)
        if returnedDict == []:
            print("error")
        return render_template("index.html", ingredients=returnedDict)
    return render_template("index.html")


@search_blueprint.route("/search_recipes", methods=["POST"])
def searchByrecipes():
    if request.method == "POST":
        ingredients = request.form.get("searchRecipes")
        # prints what the user searches for to the terminal
        print(ingredients)
        returnedDict = search_recipes(ingredients)
        # prints the 10 recipes to the terminal
        print(returnedDict)
        if returnedDict == []:
            print("error")
        return render_template("index.html", recipes=returnedDict)
    return render_template("index.html")


@search_blueprint.route("/search")
def search():
    return render_template("search.html")
