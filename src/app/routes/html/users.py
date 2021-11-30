"""
This file contains routes related to users.

So long as a user has their profile set to public, then you can view the user's profile by
visiting "/@<username>", where "<username>" is the user's username.
"""

from flask import Flask, Blueprint, render_template, abort

from ..routing_util import NoCurrentUserException, get_current_user
from ...database.database import (
    Database,
    DatabaseException,
    NoUserException,
    ProfileVisibility,
)
from ... import util

blueprint = Blueprint(
    "bp_html_users",
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
    Returns a list of saved ingredients for the specified user
    split into "liked" and "disliked" groups.
    """
    try:
        (ingredients, liked, _) = DATABASE.get_ingredients(user_id)
        liked_group = []
        disliked_group = []
        for i, ingredient in enumerate(ingredients):
            ingredient_json = ingredient.to_json()
            ingredient_json["liked"] = liked[i]

            if liked[i]:
                liked_group.append(ingredient_json)
            else:
                disliked_group.append(ingredient_json)

        return (liked_group, disliked_group)
    except DatabaseException:
        return ([], [])


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


@blueprint.route("/@<username>")
def user_profile(username):
    """
    Returns the specified user's profile, or a default page if the specified user does not exist.
    """
    current_user = None
    try:
        current_user = get_current_user().to_json()
    except NoCurrentUserException:
        pass

    userdata = None
    try:
        user = DATABASE.get_user_by_username(username)

        has_relationship = current_user is not None and DATABASE.has_relationship(
            user.id, current_user["id"]
        )

        userdata = user.to_json(shallow=(not has_relationship))

        userdata["has_relationship_with_current"] = has_relationship

        if (
            ProfileVisibility.has(
                userdata["profile_visibility"], ProfileVisibility.INTOLERANCES
            )
            or userdata["has_relationship_with_current"]
        ):
            userdata["intolerances"] = get_intolerances(user.id)

        if (
            ProfileVisibility.has(
                userdata["profile_visibility"], ProfileVisibility.SAVED_RECIPES
            )
            or userdata["has_relationship_with_current"]
        ):
            userdata["recipes"] = get_saved_recipes(user.id)

        if (
            ProfileVisibility.has(
                userdata["profile_visibility"], ProfileVisibility.SAVED_INGREDIENTS
            )
            or userdata["has_relationship_with_current"]
        ):
            (liked_ingredients, disliked_ingredients) = get_saved_ingredients(user.id)
            userdata["liked_ingredients"] = liked_ingredients
            userdata["disliked_ingredients"] = disliked_ingredients

        if (
            ProfileVisibility.has(
                userdata["profile_visibility"], ProfileVisibility.FRIENDS
            )
            or userdata["has_relationship_with_current"]
        ):
            userdata["friends"] = get_friends(user.id)
    except NoUserException:
        abort(404)
    except DatabaseException:
        abort(500)

    return render_template(
        "profile_page.html",
        userdata=userdata,
        current_userdata=current_user,
    )
