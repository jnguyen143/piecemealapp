from flask import Blueprint, render_template
import routes.util as util

profile_blueprint = Blueprint(
    "bp_profile",
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
    return profile_blueprint


@profile_blueprint.route("/profile")
def profile():
    return render_template("profile.html")
