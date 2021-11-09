from flask import Flask, Blueprint, render_template
from . import util
from database import database
from flask_login import current_user

account_blueprint = Blueprint(
    "bp_account",
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
    return account_blueprint


# For internal use only
int__db: database.Database = None


def init(db: database.Database):
    """
    Initializes this module using the provided arguments.

    Args:
        db (Database): The database object to use.
    """
    global int__db
    int__db = db


@account_blueprint.route("/account")
def account():
    return render_template("account.html", userdata=current_user.to_json())
