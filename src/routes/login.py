from flask import Flask, Blueprint, render_template, redirect
from . import util
from database import database
from flask_login import LoginManager, logout_user

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


def init(app: Flask, db: database.Database):
    """
    Initializes this module using the provided arguments.

    Args:
        app (Flask): The application object.
        db (Database): The database object to use.
    """
    global int__db
    global login_manager
    int__db = db
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(load_user)


@login_blueprint.route("/login")
def login():
    return render_template("login.html")


@login_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect("/")
