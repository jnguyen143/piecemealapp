"""
This file contains routes related to users.

So long as a user has their profile set to public, then you can view the user's profile by
visiting "/@<username>", where "<username>" is the user's username.
"""

from flask import Flask, Blueprint, render_template, abort

from app.routes.routing_util import NoCurrentUserException, get_current_user
from ...database.database import (
    Database,
    DatabaseException,
    NoUserException,
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


@blueprint.route("/@<username>")
def user_profile(username):
    """
    Returns the specified user's profile, or a default page if the specified user does not exist.
    """
    current_user = None
    try:
        current_user = get_current_user()
    except NoCurrentUserException:
        pass

    try:
        user = DATABASE.get_user_by_username(username)
        return render_template(
            "profile_page.html",
            userdata=user.to_json(),
            current_userdata=current_user.to_json(),
        )
    except NoUserException:
        abort(404)
    except DatabaseException:
        abort(500)
