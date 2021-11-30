"""
This file contains user-facing endpoints relating to account pages.
"""
from flask import Flask, Blueprint, render_template, abort
from flask_login import login_required
from ...database.database import (
    Database,
    DatabaseException,
)
from ... import util
from ..routing_util import (
    get_current_user,
    NoCurrentUserException,
)

blueprint = Blueprint(
    "bp_html_account",
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


@blueprint.route("/account")
@login_required
def account():
    """
    Returns the account page.
    """
    userdata = None
    try:
        current_user = get_current_user()
        userdata = current_user.to_json()
        userdata["friends"] = [
            x.to_json(shallow=True)
            for x in DATABASE.get_relationships_for_user(current_user.id)[0]
        ]
    except DatabaseException:
        abort(500)
    except NoCurrentUserException:
        abort(500)
    return render_template("account.html", userdata=userdata)
