"""this file contains functions for looking up recipes"""
from random import randrange
import math
from ..database.database import Database, InvalidArgumentException
from . import spoonacular
from ..routes.routing_util import InvalidEndpointArgsException, get_current_user


def get_random_recipes(database: Database, source: str = "cache", limit: int = 10):
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

    recipes = []
    if source == "cache":
        recipes = database.get_random_recipe_infos(limit)
    elif source == "external":
        recipes = spoonacular.get_random_recipes(limit)
    elif source == "mixed":
        # We have to do it this way because the values may have been truncated
        limit_external = limit / 2
        limit_cache = limit - limit_external
        external_recipes = spoonacular.get_random_recipes(limit_external)
        cached_recipes = database.get_random_recipe_infos(limit_cache)
        for recipe in external_recipes:
            recipes.append(recipe)
        for recipe in cached_recipes:
            recipes.append(recipe)
    else:
        raise InvalidArgumentException("Bad source")
    return recipes


def get_recommended_recipes(
    database: Database,
    sources: list[str] = None,
    distributions: list[int] = None,
    limit: int = 10,
):
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

    recipes = []

    # First, run through each source and try to make sure each is distributed as it should be
    if sources is None:
        sources = [
            "random",
            "friends",
            "friends_similar",
            "ingredients",
            "recently_liked",
        ]
    for i, source in enumerate(sources):
        if limit == 0:
            break
        extracted_recipes = extract_recipes(
            database,
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
            extracted_recipes = extract_recipes(database, source, None, limit, None)
            limit -= len(extracted_recipes)
            recipes += extracted_recipes

    return recipes


def extract_recipes(database, source, distribution, limit, num_sources_left):
    """
    Extracts recipes from the specified source.
    """
    if source == "recently_liked":
        return extract_recently_liked_recipes(
            database, distribution, limit, num_sources_left
        )
    if source == "friends":
        return extract_friends_recipes(database, distribution, limit, num_sources_left)
    if source == "friends_similar":
        return extract_friends_similar_recipes(
            database, distribution, limit, num_sources_left
        )
    if source == "ingredients":
        return extract_ingredients_recipes(
            database, distribution, limit, num_sources_left
        )
    if source == "random":
        return extract_random_recipes(database, distribution, limit, num_sources_left)
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


def extract_recently_liked_recipes(database, distribution, limit, num_sources_left):
    """
    Extracts recipes similar to the current user's recently liked recipes.
    """
    user = get_current_user()

    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    model_recipes = database.get_user_top_recipes(user.id, 3)

    # Get an even amount of similar recipes for each top recipe
    result = []
    for model_recipe in model_recipes:
        if len(result) == actual_limit:
            break
        similar_recipes = spoonacular.get_similar_recipes(
            model_recipe.id, actual_limit / len(model_recipes)
        )

        # Cache the results
        database.add_ingredient_infos(similar_recipes, ignore_duplicates=True)

        for recipe in similar_recipes:
            if len(result) == actual_limit:
                break
            result.append(recipe)

    return result


def extract_friends_recipes(database, distribution, limit, num_sources_left):
    """
    Extracts top recipes from a subset of the current user's friends.
    """
    user = get_current_user()

    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    top_recipes = database.get_friend_top_recipes(
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


def extract_friends_similar_recipes(database, distribution, limit, num_sources_left):
    """
    Extracts similar recipes to the top recipes from a subset of the current user's friends.
    """
    user = get_current_user()

    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    top_recipes = database.get_friend_top_recipes(
        user.id, limit_per_friend=actual_limit
    )

    result = []
    for friend_data in top_recipes:
        if len(result) == actual_limit:
            break

        if len(friend_data["recipes"]) == 0:
            continue

        # Choose a random recipe from the friend's list of top recipes
        model_recipe = friend_data["recipes"][randrange(0, len(friend_data["recipes"]))]

        # Get similar recipes to the chosen model recipe
        similar_recipes = spoonacular.get_similar_recipes(
            model_recipe.id, int(math.ceil(actual_limit / len(top_recipes)))
        )

        # Cache the results
        database.add_ingredient_infos(similar_recipes, ignore_duplicates=True)

        for recipe in similar_recipes:
            if len(result) == actual_limit:
                break
            result.append(recipe)

    return result


def extract_ingredients_recipes(database, distribution, limit, num_sources_left):
    """
    Extracts recipes which include ingredients from the current user's saved ingredients.
    """
    user = get_current_user()

    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    # Get random top 3 ingredients
    top_ingredients = database.get_user_top_ingredients(user.id, 3)

    # For each ingredient, extract a proportional amount of recipes
    result = []
    for ingredient in top_ingredients:
        if len(result) == actual_limit:
            break
        recipes = spoonacular.get_recipes_by_ingredients(
            [ingredient.name], actual_limit / len(top_ingredients)
        )

        # Cache the recipes
        database.add_recipe_infos(recipes, ignore_duplicates=True)

        for recipe in recipes:
            if len(result) == actual_limit:
                break
            result.append(recipe)

    return result


def extract_random_recipes(database, distribution, limit, num_sources_left):
    """
    Extracts random recipes.
    """
    actual_limit = get_limit_from_distribution(distribution, limit, num_sources_left)

    recipes = database.get_random_recipe_infos(actual_limit)

    return list(recipes)
