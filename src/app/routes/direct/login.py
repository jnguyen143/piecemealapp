"""
This file contains user-facing endpoints relating to login pages.
"""
from flask import Flask, Blueprint, render_template, request
from flask_login import LoginManager
from flask_login.utils import login_required, logout_user
from werkzeug.utils import redirect
from ...database.database2 import (
    Database,
)
from ... import util

blueprint = Blueprint(
    "bp_direct_login",
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
LOGIN_MANAGER: LoginManager = LoginManager()


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

    LOGIN_MANAGER.init_app(app)
    LOGIN_MANAGER.user_loader(load_user)


def load_user(user_id):
    """
    Callback function for loading a user for flask_login.
    """
    return DATABASE.get_user_by_id(user_id)


def get_login_auth_status():
    """
    Returns the authentication status for the last login attempt.
    """
    return request.args.get("login-auth-status", 0, type=int)


@blueprint.route("/login")
def login():
    """
    Returns the login page.
    """
    login_error = get_login_auth_status()
    return render_template("login.html", login_error=login_error)


@blueprint.route("/logout")
@login_required
def logout():
    """
    Logs out and returns to the index page.
    """
    logout_user()
    return redirect("/")
