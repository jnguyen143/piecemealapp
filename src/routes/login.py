from os import stat
from flask import Blueprint, render_template
import routes.util as util

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


@login_blueprint.route("/login")
def login():
    return render_template("login.html")
