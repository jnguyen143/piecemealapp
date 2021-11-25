"""
This file contains endpoints related to global recipe data.
"""
from flask import Blueprint, request, Flask

from ...database.database import (
    Database,
    DatabaseException,
    InvalidArgumentException,
    NoRecipeException,
    UserIntolerance,
)
from ... import util
from ..routing_util import (
    get_json_data,
    success_response,
    error_response,
    InvalidEndpointArgsException,
)
from ...api import spoonacular
from ...api.common import UndefinedApiKeyException

blueprint = Blueprint(
    "bp_api_global_recipes",
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


@blueprint.route("/api/recipe-info/get")
def get_recipe_info():
    """
    Returns a JSON object containing the recipe information
    for the recipe with the specified ID.

    Args:
        id (int): The ID of the target recipe.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            recipe: A Recipe object.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
            2 - No recipe exists with the provided ID.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
        "No recipe exists with the provided ID",
    ]

    recipe_id = None
    try:
        data = get_json_data(request)
        recipe_id = util.get_or_raise(data, "id", InvalidEndpointArgsException())
    except InvalidEndpointArgsException:
        return error_response(1, response_error_messages[1])

    try:
        recipe = DATABASE.get_recipe_info(recipe_id)
        return success_response(recipe.to_json())
    except NoRecipeException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/recipe-info/search")
def search_recipes():
    """
    Returns a list of recipes which match the specified search query.

    Args:
        query (str): The search query to use.
        intolerances (list[str]): The list of intolerances to use as a filter.
            This argument is optional.
        cuisines (list[str]): The list of cuisines to use as a filter.
            This argument is optional.
        diets (list[str]): The list of diets to use as a filter.
            This argument is optional.
        ingredients (list[int]): The list of Ingredient IDs to use as a filter.
            This argument is optional.
        max_prep_time (int): The maximum prep time for the recipes (in minutes).
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
        recipes: A list of Recipe objects.
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
        data = get_json_data(request)
        query = util.get_or_raise(data, "query", InvalidEndpointArgsException())
        filters["intolerances"] = parse_intolerances(data)
        filters["cuisines"] = parse_cuisines(data)
        filters["diets"] = parse_diets(data)
        filters["ingredients"] = parse_ingredients(data)
        sort_by = parse_sort_criteria(data)
    except InvalidEndpointArgsException:
        return error_response(1, response_error_messages[1])

    filters["max_prep_time"] = util.get_or_default(data, "max_prep_time", -1)
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


def parse_cuisines(data):
    """
    Parses cuisine filters from the input data for the search endpoint.
    """

    result = []
    try:
        cuisines = util.get_or_raise(data, "cuisines", InvalidEndpointArgsException())
        for cuisine in cuisines:
            result.append(spoonacular.Cuisine[str(cuisine).upper()])
    except (InvalidEndpointArgsException, KeyError):
        return None

    return None if len(result) == 0 else result


def parse_diets(data):
    """
    Parses diet filters from the input data for the search endpoint.
    """
    result = []
    try:
        diets = util.get_or_raise(data, "diets", InvalidEndpointArgsException())
        for diet in diets:
            result.append(spoonacular.Diet[str(diet).upper()])
    except (InvalidEndpointArgsException, KeyError):
        return None

    return None if len(result) == 0 else result


def parse_ingredients(data):
    """
    Parses ingredient filters from the input data for the search endpoint.
    """
    result = util.get_or_default(data, "ingredients", [])
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


@blueprint.route("/api/recipe-info/get-similar")
def get_similar_recipes():
    """
    Returns a list of recipes which are similar to the specified recipe.

    Args:
        id (int): The recipe ID to use as a reference for the recipes to retrieve.
        limit (int): The maximum number of results to return.
            This argument is optional and by default is 10.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            recipes: A list of Recipe objects.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
            2 - The specified recipe does not exist.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
        "No recipe exists with the provided ID",
    ]

    recipe_id = None
    limit = 0
    try:
        data = get_json_data(request)
        recipe_id = util.get_or_raise(data, "id", InvalidEndpointArgsException())
        limit = util.get_or_default(data, "limit", 10)
    except InvalidEndpointArgsException:
        return error_response(1, response_error_messages[1])

    try:
        if not DATABASE.recipe_info_exists(recipe_id):
            return error_response(2, response_error_messages[2])
        recipes = spoonacular.get_similar_recipes(recipe_id, limit)

        # Cache the results for future use
        DATABASE.add_recipe_infos(recipes, ignore_duplicates=True)

        return success_response({"recipes": recipes})
    except (
        spoonacular.SpoonacularApiException,
        UndefinedApiKeyException,
        DatabaseException,
    ):
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/recipe-info/get-random")
def get_random_recipes():
    """
    Returns a random list of recipes.

    Args:
        source (str): Where to get the recipes.
            This value is optional (by default it is cache) and must be one of the following:
            cache: Only look up recipes stored in PieceMeal's own database.
            external: Only look up recipes from external sources (i.e. Spoonacular).
                These results will then be cached.
            mixed: Return a mixture (approximately half and half) of cached and external recipes.
                Any external recipes will be cached once they have been retrieved.
        limit (int): The maximum number of results to return.
            This argument is optional and by default is 10.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            recipes: A list of Recipe objects.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "Corrupt input arguments",
    ]

    data = None
    source = "cache"
    limit = 10
    try:
        data = get_json_data(request)
        source = util.get_or_default(data, "source", "cache")
        limit = util.get_or_default(data, "limit", 10)
    except InvalidEndpointArgsException:
        pass  # If no data was passed, that's okay; all of the fields are optional.

    try:
        recipes = []
        if source == "cache":
            recipes = DATABASE.get_random_recipe_infos(limit)
        elif source == "external":
            recipes = spoonacular.get_random_recipes(limit)
        elif source == "mixed":
            # We have to do it this way because the values may have been truncated
            limit_external = limit / 2
            limit_cache = limit - limit_external

            external_recipes = spoonacular.get_random_recipes(limit_external)
            cached_recipes = DATABASE.get_random_recipe_infos(limit_cache)

            for recipe in external_recipes:
                recipes.append(recipe)
            for recipe in cached_recipes:
                recipes.append(recipe)
        else:
            return error_response(1, response_error_messages[1])
        return success_response({"recipes": recipes})
    except InvalidArgumentException:
        return error_response(1, response_error_messages[1])
    except (
        DatabaseException,
        spoonacular.SpoonacularApiException,
        UndefinedApiKeyException,
    ):
        return error_response(0, response_error_messages[0])
