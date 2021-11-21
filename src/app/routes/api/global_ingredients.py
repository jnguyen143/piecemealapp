"""
This file contains endpoints related to global ingredient data.
"""
from flask import Blueprint, request, Flask
from ...database.database2 import (
    Database,
    DatabaseException,
    NoIngredientException,
    UserIntolerance,
)
from ... import util
from ..routing_util import (
    get_post_json,
    success_response,
    error_response,
    InvalidEndpointArgsException,
)
from ...api import spoonacular
from ...api.common import UndefinedApiKeyException

blueprint = Blueprint(
    "bp_api_global_ingredients",
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


@blueprint.route("/api/ingredient-info/get")
def get_ingredient_info():
    """
    Returns a JSON object containing the ingredient information
    for the ingredient with the specified ID.

    Args:
        id (int): The ID of the target ingredient.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            ingredient: An Ingredient object.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
            2 - No ingredient exists with the provided ID.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
        "No ingredient exists with the provided ID",
    ]

    ingredient_id = None
    try:
        data = get_post_json(request)
        ingredient_id = util.get_or_raise(data, "id", InvalidEndpointArgsException())
    except InvalidEndpointArgsException:
        return error_response(1, response_error_messages[1])

    try:
        ingredient = DATABASE.get_ingredient_info(ingredient_id)
        return success_response(ingredient.to_json())
    except NoIngredientException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/ingredient-info/search")
def search_ingredients():
    """
    Returns a list of ingredients which match the specified search query.

    Args:
        query (str): The search query to use.
        intolerances (list[str]): The list of intolerances to use as a filter.
            This argument is optional.
        sort_by (str): The criteria to use to sort the results.
            This argument is optional.
        offset (int): The offset into the results to start at.
            This argument is optional and by default is 0.
        limit (int): The maximum number of results to return.
            This argument is optional and by default is 10.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            ingredients: A list of Ingredient objects.
            total_results: An integer describing the maximum number of available results.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
    ]

    data = None
    query = None
    filters = {}
    sort_by = None
    try:
        data = get_post_json(request)
        query = util.get_or_raise(data, "query", InvalidEndpointArgsException())
        filters["intolerances"] = parse_intolerances(data)
        sort_by = parse_sort_criteria(data)
    except InvalidEndpointArgsException:
        return error_response(1, response_error_messages[1])

    offset = util.get_or_default(data, "offset", 0)
    limit = util.get_or_default(data, "limit", 10)

    try:
        results = spoonacular.search_recipes(
            query,
            filters,
            sort_by,
            offset,
            limit,
        )

        # Cache the results for future use
        DATABASE.add_recipe_infos(results[0], ignore_duplicates=True)

        return success_response(results)
    except (
        DatabaseException,
        spoonacular.SpoonacularApiException,
        UndefinedApiKeyException,
    ):
        return error_response(0, response_error_messages[0])


def parse_intolerances(data):
    """
    Parses intolerance filters from the input data for the search endpoint.
    """
    result = []
    try:
        intolerances = util.get_or_raise(
            data, "intolerances", InvalidEndpointArgsException()
        )
        for intolerance in intolerances:
            result.append(UserIntolerance[str(intolerance).upper()])
    except (InvalidEndpointArgsException, KeyError):
        return None

    return None if len(result) == 0 else result


def parse_sort_criteria(data):
    """
    Parses sort criteria from the input data for the search endpoint.
    """
    try:
        criteria = util.get_or_raise(data, "sort_by", InvalidEndpointArgsException())
        return spoonacular.SortCriteria[str(criteria).upper()]
    except (InvalidEndpointArgsException, KeyError):
        return None
