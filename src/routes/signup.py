from os import stat
from flask import Blueprint, render_template
import routes.util as util

signup_blueprint = Blueprint(
    "bp_signup",
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
    return signup_blueprint


@signup_blueprint.route("/signup")
def login():
    return render_template("signup.html")
