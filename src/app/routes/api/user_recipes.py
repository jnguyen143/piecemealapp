"""
This file contains endpoints related to user recipe data.
"""
from random import randrange
from flask import Blueprint, request, Flask
from flask_login import login_required
from ...api import spoonacular

from ...database.database import (
    Database,
    DatabaseException,
    InvalidArgumentException,
)
from ... import util
from ..routing_util import (
    get_json_data,
    success_response,
    error_response,
    get_current_user,
    InvalidEndpointArgsException,
    NoCurrentUserException,
)

blueprint = Blueprint(
    "bp_api_user_recipes",
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


def validate_recipe_object(recipe_obj: dict):
    """
    Checks the provided recipe object to ensure it has all of the necessary fields.

    If any of the required fields are missing, this function will raise an exception.
    """
    recipe_id = util.get_or_raise(recipe_obj, "id", InvalidEndpointArgsException())
    name = util.get_or_raise(recipe_obj, "name", InvalidEndpointArgsException())
    image = util.get_or_raise(recipe_obj, "image", InvalidEndpointArgsException())

    if recipe_id is None or name is None or image is None:
        raise InvalidEndpointArgsException()


@blueprint.route("/api/user-recipes/get")
@login_required
def get_user_recipes():
    """
    Returns a list of recipe objects which the current user has saved.

    Args:
        offset (int): The offset into the list to start at.
            This value must be greater than or equal to 0 and is optional (by default, it is 0).
        limit (int): The maximum number of recipes to return.
            This value must be greater than or equal to 0 and is optional
            (by default, it is 0, which tells the server to return all of
            the current user's recipes).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            recipes: A list of Recipe objects. This list will be empty if
                the user has no saved recipes.
            total_recipes (int): A value describing the total amount of
                recipes the current user has.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
    ]

    data = None
    try:
        data = get_json_data(request)
    except InvalidEndpointArgsException:
        pass  # If no data was passed, that's okay; all of the fields are optional.

    offset = 0
    limit = 0

    if data is not None:
        offset = util.get_or_default(data, "offset", 0)
        limit = util.get_or_default(data, "limit", 0)

    try:
        user_id = get_current_user().id

        recipes = DATABASE.get_recipes(user_id, offset, limit)
        return success_response(
            {
                "recipes": [recipe.to_json() for recipe in recipes[0]],
                "total_recipes": recipes[1],
            }
        )
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-recipes/add", methods=["POST"])
@login_required
def add_user_recipe():
    """
    Adds the specified recipe to the current user's list of saved recipes.

    Args:
        recipe: The recipe to save, which must be a Recipe object
            (the summary and full_summary fields are optional).

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The user already has the specified recipe.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "Duplicate recipe entry",
    ]

    try:
        data = get_json_data(request, "POST")
        recipe = util.get_or_raise(data, "recipe", InvalidEndpointArgsException())

        validate_recipe_object(recipe)

        user_id = get_current_user().id

        result = DATABASE.add_recipe(user_id, recipe)

        if not result:
            return error_response(3, response_error_messages[3])
        return success_response()
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(2, response_error_messages[2])
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-recipes/delete", methods=["POST"])
@login_required
def delete_user_recipe():
    """
    Deletes the specified recipe from the current user's list of saved recipes.

    Args:
        id (int): The ID of the recipe to delete.

    Returns:
        On success, a JSON object containing the following field:
            success (bool): Whether the request was successfully completed.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
            3 - The user does not have the specified recipe.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
        "No recipe entry exists for the current user with the specified ID",
    ]

    try:
        data = get_json_data(request, "POST")
        recipe_id = util.get_or_raise(data, "id", InvalidEndpointArgsException())

        user_id = get_current_user().id

        result = DATABASE.delete_recipe(user_id, recipe_id)

        if result:
            return success_response()
        return error_response(3, response_error_messages[3])
    except (InvalidEndpointArgsException, InvalidArgumentException):
        return error_response(2, response_error_messages[2])
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-recipes/get-top")
@login_required
def get_user_top_recipes():
    """
    Returns a list of a random selection from the current user's most recently liked recipes.

    The algorithm will look at only the most recently liked recipes and will only retrieve
    up to the specified limit of recipes.

    Args:
        limit (int): The maximum number of recipes to return.
            This value must be greater than or equal to 0 and is optional
            (by default, the limit is 5).

    Returns:
    On success, a JSON object containing the following fields:
        success (bool): Whether the request was successfully completed.
        recipes: A list of Recipe objects. This list is guaranteed to
            be less than or equal to the specified limit.

    On failure, the possible error codes are:
        0 - A general exception occurred.
        1 - There is no user currently logged in.
        2 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
    ]

    data = None
    try:
        data = get_json_data(request)
    except InvalidEndpointArgsException:
        pass

    limit = 5
    if data is not None:
        limit = util.get_or_default(data, "limit", 5)

    try:
        user_id = get_current_user().id

        recipes = DATABASE.get_user_top_recipes(user_id, limit)

        return success_response({"recipes": [recipe.to_json() for recipe in recipes]})
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-recipes/get-friend-top")
@login_required
def get_friend_top_recipes():
    """
    Returns a list of user/recipe list pairs generated based off of the liked recipes
    of the current user's friends.

    The algorithm will look at only the most recently liked recipes and will only retrieve
    up to the specified limit of recipes per friend.

    Args:
        friend_limit (int): The maximum amount of friends to sample from.
            This value must be greater than or equal to 0 and is optional
            (by default, the limit is 5).
        limit_per_friend (int): The maximum amount of recipes to retrieve
            per friend. This value must be greater than or equal to 0 and
            is optional (by default, the limit is 5).

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            friends: A list of objects containing the following fields:
                friend: A User object describing the associated friend.
                recipes: A list of Recipe objects representing the friend's top recipes.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
    ]

    data = None
    try:
        data = get_json_data(request)
    except InvalidEndpointArgsException:
        pass

    friend_limit = 5
    limit_per_friend = 5
    if data is not None:
        friend_limit = util.get_or_default(data, "friend_limit", 5)
        limit_per_friend = util.get_or_default(data, "limit_per_friend", 5)

    try:
        user_id = get_current_user().id

        friends = DATABASE.get_friend_top_recipes(
            user_id, friend_limit, limit_per_friend
        )

        result = []

        for friend in friends:
            result.append(
                {
                    "friend": friend["user"].to_json(shallow=True),
                    "recipes": [recipe.to_json() for recipe in friend["recipes"]],
                }
            )

        return success_response({"friends": result})
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidArgumentException:
        return error_response(2, response_error_messages[2])
    except DatabaseException:
        return error_response(0, response_error_messages[0])


@blueprint.route("/api/user-recipes/get-recommended")
def get_recommended_recipes():
    """
    Returns a list of recipe objects based on calculated recommendations for the current user.

    This endpoint employs a set of algorithms to determine which recipes
    to retrieve and from where. These include:
        Based on recently liked: Chooses similar recipes to the user's most recently like recipes.
        What the user's friends like: Chooses recipes from the most recently liked recipes
            of a subset of the user's friends.
        Based on what the user's friends like: Chooses similar recipes to the most recently
            liked recipes from a subset of the user's friends.
        Based on liked ingredients: Chooses recipes that include the user's most recently
            liked ingredients.
        Try something new: Chooses recipes at random (the same as
            calling `/api/recipe-info/get-random`).

    Args:
        sources (list[str]): The list of sources from which the algorithm should generate recipes.
            This argument is optional and can only consist of one or more of the following strings:
            recently_liked: Chooses similar recipes to the user's most recently like recipes.
            friends: Chooses recipes from the most recently liked
                recipes of a subset of the user's friends.
            friends_similar: Chooses similar recipes to the most recently liked recipes from
                a subset of the user's friends.
            ingredients: Chooses recipes that include the user's most recently liked ingredients.
            random: Chooses recipes at random (the same as calling /api/recipe-info/get-random).
        distributions (list[int]): The list of distributions for the amount of recipes that
            should be generated per source. This argument is optional and if present,
            the number of elements in this list must equal the number of elements in sources.
            If the limit is defined as -1, each distribution is an exact limit per source.
            Otherwise, each distribution represents a percentage of the overall limit.
        limit (int): The maximum number of recipes to return. This value is optional
            and is 10 by default. If the distributions list is
            also defined, then each distribution in the list represents a percentage of this value.

    Returns:
        On success, a JSON object containing the following fields:
            success (bool): Whether the request was successfully completed.
            recipes: A list of Recipe objects. This list will be empty if the algorithm was unable
                to retrieve any recipes for the specified sources and distributions.

        On failure, the possible error codes are:
            0 - A general exception occurred.
            1 - There is no user currently logged in.
            2 - The input arguments were missing or otherwise corrupted.
    """

    response_error_messages = [
        "Unknown error",
        "No user logged in",
        "Corrupt input arguments",
    ]

    sources = None
    distributions = None
    limit = 10

    try:
        data = get_json_data(request)
        sources = util.get_or_default(
            data,
            "sources",
            ["recently_liked", "friends", "friends_similar", "ingredients", "random"],
        )
        distributions = util.get_or_default(
            data, "distributions", [100 / len(sources) for _ in sources]
        )
        limit = util.get_or_default(data, "limit", 10)
    except InvalidEndpointArgsException:
        pass  # All arguments are optional, so it's okay if there's an error

    recipes = []

    try:
        # First, run through each source and try to make sure each is distributed as it should be
        for i, source in enumerate(sources):
            if limit == 0:
                break
            extracted_recipes = extract_recipes(
                source,
                None if distributions is None else distributions[i],
                limit,
                len(sources) - i,
            )
            limit -= len(extracted_recipes)
            recipes += extracted_recipes

        # If there are still recipes to be retrieved, get as many recipes as possible
        # from each source until it's done
        if limit > 0:
            for i, source in enumerate(sources):
                if limit == 0:
                    break
                extracted_recipes = extract_recipes(source, None, limit, None)
                limit -= len(extracted_recipes)
                recipes += extracted_recipes
    except NoCurrentUserException:
        return error_response(1, response_error_messages[1])
    except InvalidEndpointArgsException:
        return error_response(2, response_error_messages[2])
    except (DatabaseException, spoonacular.SpoonacularApiException):
        return error_response(0, response_error_messages[0])

    return success_response({"recipes": recipes})


def extract_recipes(source, distribution, limit, num_sources_left):
    """
    Extracts recipes from the specified source.
    """
    if source == "recently_liked":
        return extract_recently_liked_recipes(distribution, limit, num_sources_left)
    if source == "friends":
        return extract_friends_recipes(distribution, limit, num_sources_left)
    if source == "friends_similar":
        return extract_friends_similar_recipes(distribution, limit, num_sources_left)
    if source == "ingredients":
        return extract_ingredients_recipes(distribution, limit, num_sources_left)
    if source == "random":
        return extract_random_recipes(distribution, limit, num_sources_left)
    raise InvalidEndpointArgsException(f'Invalid source "{source}"')


def get_limit_from_distribution(distribution, limit, num_sources_left):
    """
    Returns the limit based on the distribution.
    """
    if distribution is None and num_sources_left is None:
        return limit
    if distribution is None:
        return limit / num_sources_left
    if num_sources_left is None:
        return int((float(distribution) / 100) * limit)
    raise InvalidEndpointArgsException()


def get_random_list_distribution(lst: list, count: int):
    """
    Returns a random distribution of `count` number of elements from the provided list.
    """
    max_count = min(count, len(lst))
    chosen_indices = []
    result = []
    tries = 0
    max_tries = 20

    while len(result) < max_count and tries < max_tries:
        index = randrange(0, len(lst))
        if index in chosen_indices:
            tries += 1
            continue
        tries = 0
        chosen_indices.append(index)
        result.append(lst[index])

    if len(result) < max_count:
        for i, element in enumerate(lst):
            if i in chosen_indices:
                continue
            result.append(element)

    return result


def extract_recently_liked_recipes(distribution, limit, num_sources_left):
    """
    Extracts recipes similar to the current user's recently liked recipes.
    """
    user = get_current_user()

    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    model_recipes = DATABASE.get_user_top_recipes(user.id, 3)

    # Get an even amount of similar recipes for each top recipe
    result = []
    for model_recipe in model_recipes:
        if len(result) == actual_limit:
            break
        similar_recipes = spoonacular.get_similar_recipes(
            model_recipe.id, actual_limit / len(model_recipes)
        )

        # Cache the results
        DATABASE.add_ingredient_infos(similar_recipes, ignore_duplicates=True)

        for recipe in similar_recipes:
            if len(result) == actual_limit:
                break
            result.append(recipe)

    return result


def extract_friends_recipes(distribution, limit, num_sources_left):
    """
    Extracts top recipes from a subset of the current user's friends.
    """
    user = get_current_user()

    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    top_recipes = DATABASE.get_friend_top_recipes(
        user.id, limit_per_friend=actual_limit
    )

    result = []
    for friend_data in top_recipes:
        if len(result) == actual_limit:
            break

        # Get the appropriate amount of recipes in a random distribution
        num_target_recipes = actual_limit / len(top_recipes)
        actual_recipes = get_random_list_distribution(
            friend_data["recipes"], num_target_recipes
        )

        for recipe in actual_recipes:
            if len(result) == actual_limit:
                break
            result.append(recipe.to_json())

    return result


def extract_friends_similar_recipes(distribution, limit, num_sources_left):
    """
    Extracts similar recipes to the top recipes from a subset of the current user's friends.
    """
    user = get_current_user()

    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    top_recipes = DATABASE.get_friend_top_recipes(
        user.id, limit_per_friend=actual_limit
    )

    result = []
    for friend_data in top_recipes:
        if len(result) == actual_limit:
            break

        # Choose a random recipe from the friend's list of top recipes
        model_recipe = friend_data["recipes"][randrange(0, len(friend_data["recipes"]))]

        # Get similar recipes to the chosen model recipe
        similar_recipes = spoonacular.get_similar_recipes(
            model_recipe.id, actual_limit / len(top_recipes)
        )

        # Cache the results
        DATABASE.add_ingredient_infos(similar_recipes, ignore_duplicates=True)

        for recipe in similar_recipes:
            if len(result) == actual_limit:
                break
            result.append(recipe)

    return result


def extract_ingredients_recipes(distribution, limit, num_sources_left):
    """
    Extracts recipes which include ingredients from the current user's saved ingredients.
    """
    user = get_current_user()

    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    # Get random top 3 ingredients
    top_ingredients = DATABASE.get_user_top_ingredients(user.id, 3)

    # For each ingredient, extract a proportional amount of recipes
    result = []
    for ingredient in top_ingredients:
        if len(result) == actual_limit:
            break
        recipes = spoonacular.get_recipes_by_ingredients(
            [ingredient.name], actual_limit / len(top_ingredients)
        )

        # Cache the recipes
        DATABASE.add_recipe_infos(recipes, ignore_duplicates=True)

        for recipe in recipes:
            if len(result) == actual_limit:
                break
            result.append(recipe)

    return result


def extract_random_recipes(distribution, limit, num_sources_left):
    """
    Extracts random recipes.
    """
    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    recipes = DATABASE.get_random_recipe_infos(actual_limit)

    return [recipe.to_json() for recipe in recipes]
