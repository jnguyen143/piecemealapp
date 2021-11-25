"""
This file contains user-facing endpoints relating to signup pages.
"""
from flask import Flask, Blueprint, render_template, request
from ...database.database import (
    Database,
)
from ... import util

blueprint = Blueprint(
    "bp_direct_signup",
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


def get_signup_auth_status():
    """
    Returns the authentication status for the last signup attempt.
    """
    return request.args.get("signup-auth-status", 0, type=int)


@blueprint.route("/signup")
def signup():
    """
    Returns the signup page.
    """
    signup_error = get_signup_auth_status()
    return render_template("signup.html", signup_error=signup_error)
