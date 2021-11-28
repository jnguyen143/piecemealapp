"""
This file contains user-facing endpoints relating to profile pages.
"""
from flask import Flask, Blueprint, render_template
from flask_login import login_required
from ...database.database import Database, DatabaseException, ProfileVisibility
from ... import util
from ..routing_util import get_current_user

blueprint = Blueprint(
    "bp_html_profile",
    __name__,
    template_folder=util.get_templates_folder(),
    static_folder=util.get_static_folder(),
)


def get_blueprint() -> Blueprint:
    """
    Returns the `Blueprint` object which stores all of the functions in this file.

    All routing files have the same function to retrieve their blueprints.

    Returns:
        The blueprint object for this file.
    """
    return blueprint


DATABASE: Database = None


def init(app: Flask, database: Database):
    """
    Initializes this module.

    Args:
        app (Flask): The Flask application object.
        database (Database): The database object.
    """
    # pylint: disable=global-statement
    # We need to modify the global database object using this function
    global DATABASE

    DATABASE = database

    app.register_blueprint(get_blueprint())


def get_intolerances(user_id):
    """
    Returns a list of intolerances for the specified user.
    """
    try:
        return [
            intolerance.to_json()
            for intolerance in DATABASE.get_intolerances(user_id)[0]
        ]
    except DatabaseException:
        return []


def get_saved_recipes(user_id):
    """
    Returns a list of saved recipes for the specified user.
    """
    try:
        return [recipe.to_json() for recipe in DATABASE.get_recipes(user_id)[0]]
    except DatabaseException:
        return []


def get_saved_ingredients(user_id):
    """
    Returns a list of saved ingredients for the specified user.
    """
    try:
        return [
            ingredient.to_json() for ingredient in DATABASE.get_ingredients(user_id)[0]
        ]
    except DatabaseException:
        return []


def get_friends(user_id):
    """
    Returns a list of friends for the specified user.
    """
    try:
        return [
            friend.to_json(shallow=True)
            for friend in DATABASE.get_relationships_for_user(user_id)[0]
        ]
    except DatabaseException:
        return []


def get_friend_requests(user_id):
    """
    Returns a list of friend requests for which the specified user is a recipient.
    """
    try:
        return [
            friend.to_json(shallow=True)
            for friend in DATABASE.get_friend_requests_for_target(user_id)[0]
        ]
    except DatabaseException:
        return []


@blueprint.route("/profile")
@login_required
def profile():
    """
    Returns the profile page.
    """
    current_user = get_current_user()

    userdata = current_user.to_json()

    userdata["recipes"] = get_saved_recipes(current_user.id)
    userdata["ingredients"] = get_saved_ingredients(current_user.id)
    userdata["intolerances"] = get_intolerances(current_user.id)
    userdata["friends"] = get_friends(current_user.id)
    userdata["friend_requests"] = get_friend_requests(current_user.id)

    return render_template(
        "my_profile.html",
        current_userdata=userdata,
        permissions=ProfileVisibility.to_json(current_user.profile_visibility),
    )

    """current_user = get_current_user()
    (recipes, _) = DATABASE.get_recipes(current_user.id)
    (ingredients, _) = DATABASE.get_ingredients(current_user.id)

    if len(recipes) == 0:
        try:
            recipes = spoonacular.get_recommended_recipes()
        except spoonacular.SpoonacularApiException:
            pass

    return render_template(
        "my_profile.html",
        recipes=[recipe.to_json() for recipe in recipes],
        has_recipes=len(recipes) > 0,
        ingredients=[ingredient.to_json() for ingredient in ingredients],
        has_ingredient=len(ingredients) > 0,
        userdata=current_user.to_json(shallow=True),
    )"""
