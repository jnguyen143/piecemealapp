from flask import Blueprint, redirect
from flask_login import logout_user
from . import util


logout_blueprint = Blueprint(
    "bp_logout",
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
    return logout_blueprint


@logout_blueprint.route("/logout")
def logout():
    logout_user()
    return redirect("/")
