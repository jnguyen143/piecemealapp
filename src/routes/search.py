from flask import Blueprint, render_template
import routes.util as util

search_blueprint = Blueprint(
    "bp_search",
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
    return search_blueprint


@search_blueprint.route("/search")
def search():
    return render_template("search.html")
