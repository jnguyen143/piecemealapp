import flask
from flask import Blueprint, render_template, request
import routes.util as util
import api.spoonacular

# import spoonacular somehow

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


@search_blueprint.route("/search_ingredients")
def search_ingredients():
    return render_template("search.html")


@search_blueprint.route("/search_recipes", methods=["POST"])
def search_recipes():
    if flask.request.method == "POST":
        ingredients = flask.request.form.get("searchRecipes")
        # prints what the user searches for to the terminal
        #
        print(ingredients)
        returnedDict = api.spoonacular.search_recipes(ingredients)
        # prints the 10 recipes to the terminal
        print(returnedDict)
        return render_template("index.html", recipes=returnedDict)
    return render_template("index.html")


@search_blueprint.route("/search")
def search():
    return render_template("search.html")
