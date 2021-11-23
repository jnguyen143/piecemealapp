from flask_login import current_user
from flask import Blueprint, render_template, request
from flask.json import jsonify
from . import util
# pylint: disable=import-error
        # This import is valid
from database import database
from . import util


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
    userdata = current_user.to_json()
    userdata["friends"] = [
        x.to_json() for x in int__db.get_relationships_for_user(current_user.id)
    ]

    return render_template("account.html", userdata=current_user.to_json())


@account_blueprint.route("/api/account/profile")
def profile():
    return render_template("account/profile.html", userdata=current_user.to_json())


@account_blueprint.route("/api/account/friends")
def friends():
    friends = [
        # Don't give all of the user's fields to the html page; some of them should be kept private (like their email)
        {
            "id": friend.id,
            "username": friend.username,
            "given_name": friend.given_name,
            "family_name": friend.family_name,
        }
        for friend in int__db.get_relationships_for_user(current_user.id)
    ]
    friend_requests = [
        {
            "id": request.id,
            "username": request.username,
            "given_name": request.given_name,
            "family_name": request.family_name,
        }
        for request in int__db.get_friend_requests_for_target_user(current_user.id)
    ]
    return render_template(
        "account/friends.html",
        userdata=current_user.to_json(),
        friends=friends,
        friend_requests=friend_requests,
    )


@account_blueprint.route("/api/account/recipes")
def recipes():
    return render_template("account/recipes.html", userdata=current_user.to_json())


@account_blueprint.route("/api/account/ingredients")
def ingredients():
    return render_template("account/ingredients.html", userdata=current_user.to_json())


@account_blueprint.route("/api/account/intolerances")
def intolerances():
    return render_template("account/intolerances.html", userdata=current_user.to_json())


@account_blueprint.route("/api/account/search-users")
def search_users():
    search_by = None
    query = None

    try:
        search_by = request.args.get("search_by", type=str)
        query = request.args.get("query", type=str)
    except:
        search_by = "username"
        query = ""

    users = []
    if search_by == "name":
        for user in int__db.search_users_by_name(query):
            if user.id != current_user.id:
                users.append(
                    {
                        "id": user.id,
                        "username": user.username,
                        "given_name": user.given_name,
                        "family_name": user.family_name,
                    }
                )
    elif search_by == "username":
        for user in int__db.search_users_by_username(query):
            if user.id != current_user.id:
                users.append(
                    {
                        "id": user.id,
                        "username": user.username,
                        "given_name": user.given_name,
                        "family_name": user.family_name,
                    }
                )

    return render_template("account/search_users.html", search_results=users)
