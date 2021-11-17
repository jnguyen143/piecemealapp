from flask import Flask, Blueprint, render_template, request
from . import util
from database import database
from flask_login import LoginManager, logout_user

# pylint: disable=C0103
login_blueprint = Blueprint(
    "bp_login",
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
    return login_blueprint


# For internal use only
int__db: database.Database = None
login_manager: LoginManager = None


def load_user(username):
    """
    Callback for loading the user whenever the site is refreshed.
    """
    return int__db.get_user(username)


# pylint: disable=C0103
def init(app: Flask, db: database.Database):
    """
    Initializes this module using the provided arguments.
    Args:
        app (Flask): The application object.
        db (Database): The database object to use.
    """
    # pylint: disable=C0103
    global int__db
    global login_manager
    int__db = db
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(load_user)


def get_login_auth_status():
    return request.args.get("login-auth-status", 0, type=int)


@login_blueprint.route("/login")
def login():
    login_error = get_login_auth_status()
    return render_template("login.html", login_error=login_error)
