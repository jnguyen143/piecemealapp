# pylint: disable=too-many-lines
# All of the Spoonacular calls need to go in here

"""
==================== SPOONACULAR API ====================
This file defines the functions necessary to communicate with the Spoonacular API.
Before any of the functions in this file can be called,
you must ensure that the `SPOONACULAR_API_KEY` environment variable has been defined.
"""

from enum import Enum
from os import getenv
import re

from .common import (
    api_get_json,
    RequestException,
    MalformedResponseException,
    UndefinedApiKeyException,
)


class SpoonacularApiException(Exception):
    """
    Raised if there is a problem making a Spoonacular API call.
    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message


class Intolerance(Enum):
    """
    The available intolerances that can be fed to the Spoonacular API calls,
    such as for `search_recipes()`.
    """

    DAIRY = "Dairy"
    EGG = "Egg"
    GLUTEN = "Gluten"
    GRAIN = "Grain"
    PEANUT = "Peanut"
    SEAFOOD = "Seafood"
    SESAME = "Sesame"
    SHELLFISH = "Shellfish"
    SOY = "Soy"
    SULFITE = "Sulfite"
    TREE_NUT = "Tree Nut"
    WHEAT = "Wheat"

    @classmethod
    def has(cls, value):
        """
        Returns true if this enum has the specified value.
        """
        return value in cls


class Cuisine(Enum):
    """
    The available cuisines that can be fed to the Spoonacular API calls,
    such as for `search_recipes()`.
    """

    AFRICAN = "African"
    AMERICAN = "American"
    BRITISH = "British"
    CAJUN = "Cajun"
    CARIBBEAN = "Caribbean"
    CHINESE = "Chinese"
    EASTERN_EUROPEAN = "Eastern European"
    EUROPEAN = "European"
    FRENCH = "French"
    GERMAN = "German"
    GREEK = "Greek"
    INDIAN = "Indian"
    IRISH = "Irish"
    ITALIAN = "Italian"
    JAPANESE = "Japanese"
    JEWISH = "Jewish"
    KOREAN = "Korean"
    LATIN_AMERICAN = "Latin American"
    MEDITERRANEAN = "Mediterranean"
    MEXICAN = "Mexican"
    MIDDLE_EASTERN = "Middle Eastern"
    NORDIC = "Nordic"
    SOUTHERN = "Southern"
    SPANISH = "Spanish"
    THAI = "Thai"
    VIETNAMESE = "Vietnamese"


class Diet(Enum):
    """
    The available diets that can be fed to the Spoonacular API calls,
    such as for `search_recipes()`.
    """

    GLUTEN_FREE = "Gluten Free"
    KETOGENIC = "Ketogenic"
    VEGETARIAN = "Vegetarian"
    LACTO_VEGETARIAN = "Lacto-Vegetarian"
    OVO_VEGETARIAN = "Ovo-Vegetarian"
    VEGAN = "Vegan"
    PESCETARIAN = "Pescetarian"
    PALEO = "Paleo"
    PRIMAL = "Primal"
    LOW_FODMAP = "Low FODMAP"
    WHOLE30 = "Whole30"


class SortCriteria(Enum):
    """
    The available criteria used to sort the results returned by `search_recipes()`.
    """

    POPULARITY = "popularity"
    HEALTHINESS = "healthiness"
    PRICE = "price"
    TIME = "time"
    RANDOM = "random"
    MAX_USED_INGREDIENTS = "max-used-ingredients"
    MIN_MISSING_INGREDIENTS = "min-missing-ingredients"
    CALORIES = "calories"
    CARBOHYDRATES = "carbohydrates"
    TOTAL_FAT = "total-fat"
    PROTEIN = "protein"
    SUGAR = "sugar"
    SODIUM = "sodium"


class Recipe:
    """
    Represents a recipe.

    Attributes:
        id (int): The internal ID of the recipe.
        name (str): The display name of the recipe.
        image (str): The URL which points to an image for the recipe.
        prep_time (int): The amount of time it takes to prepare and cook this recipe (in minutes).
        servings (int): The amount of servings for this recipe.
        source_url (str): The source (i.e. external) URL for this recipe.
        cuisines (list[Cuisine]): The list of cuisines to which this recipe belongs.
        diets (list[Diet]): The list of diets this recipe supports.
        gluten_free (bool): Whether this recipe is gluten free.
        ketogenic (bool): Whether this recipe is ketogenic.
        low_fodmap (bool): Whether this recipe is low-FODMAP.
        vegan (bool): Whether this recipe is vegan.
        vegetarian (bool): Whether this recipe is vegetarian.
        whole30 (bool): Whether this recipe is Whole30.
        healthy (bool): Whether this recipe is considered healthy.
        popular (bool): Whether this recipe is considered popular.
        summary (str): A string containing the summary description for the recipe
        ingredients (list): The list of ingredients (and their amounts) for this recipe.
            Each ingredient is a dictionary consisting of the following values:
                - id (int): The ID of the ingredient.
                - name (str): The display name of the ingredient.
                - amount (float): The amount of this ingredient to include in the recipe.
                - unit (str): The unit to use for the associated amount.
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    # We need all of the specified attributes.
    # Also, this is a POD type; we don't need methods for that.

    def __init__(self, args):
        self.id = args["id"]
        self.name = args["title"]
        self.image = args["image"]
        self.prep_time = args["readyInMinutes"]
        self.servings = args["servings"]
        self.source_url = args["sourceUrl"]
        self.cuisines = [Cuisine(x) for x in args["cuisines"]]
        self.diets = [Diet(x) for x in args["diets"]]
        self.gluten_free = args["gluten_free"]
        self.ketogenic = args["ketogenic"]
        self.low_fodmap = args["lowFodmap"]
        self.vegan = args["vegan"]
        self.vegetarian = args["vegetarian"]
        self.whole30 = args["whole30"]
        self.healthy = args["veryHealthy"]
        self.popular = args["veryPopular"]
        self.summary = args["summary"]

        ingredients = []
        for x in args["extendedIngredients"]:
            ingredients.append(
                {
                    "id": x["id"],
                    "name": x["name"],
                    "amount": x["measures"]["us"]["amount"],
                    "unit": x["measures"]["us"]["unitShort"],
                }
            )

        self.ingredients = ingredients


class Ingredient:
    """
    Represents an ingredient.

    Attributes:
        id (int): The internal ID of the ingredient.
        name (str): The display name of the ingredient.
        image (str): The URL which points to an image for the ingredient.
        calories (float): The amount of calories in the ingredient.
        fat (float): The amount of total fat in the ingredient (in grams).
        carbs (float): The amount of total carbohydrates in the ingredient (in grams).
        sugar (float): The amount of sugar in the ingredient (in grams).
        cholesterol (float): The amount of cholesterol in the ingredient (in grams).
        protein (float): The amount of protein in the ingredient (in grams).
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    # We need all of the specified attributes.
    # Also, this is a POD type; we don't need methods for that.

    def __init__(self, args):
        self.id = args["id"]
        self.name = args["title"]
        self.image = args["image"]
        for x in args["nutrition"]["nutrients"]:
            if x["name"] == "Calories":
                self.calories = x["amount"]
            elif x["name"] == "Fat":
                self.fat = x["amount"]
            elif x["name"] == "Carbohydrates":
                self.carbs = x["amount"]
            elif x["name"] == "Sugar":
                self.sugar = x["amount"]
            elif x["name"] == "Cholesterol":
                self.cholesterol = x["amount"]
            elif x["name"] == "Protein":
                self.protein = x["amount"]


# The ID of the environment variable which holds the key for the Spoonacular API.
SPOONACULAR_API_KEY_NAME = "SPOONACULAR_API_KEY"

# The root endpoint URL for all Spoonacular API calls.
SPOONACULAR_API_ROOT_ENDPOINT = "https://api.spoonacular.com/"


def get_api_key() -> str:
    """
    Returns the Spoonacular API key.

    Returns:
        A string containing the Spoonacular API key.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
    """
    key = getenv(SPOONACULAR_API_KEY_NAME)

    if key is None:
        raise UndefinedApiKeyException("Undefined Spoonacular API key")

    return key


def list_to_comma_separated_string(lst: list) -> str:
    """
    Returns the list of objects as a comma-separated string.
    If the list is empty, this function will return an empty string.
    """
    result = ""
    for i, n in enumerate(lst):
        if i > 0:
            result += ","
        result += str(n)
    return result


# Function to clean html formatted string within JSON response item
def clean_summary(summary):
    """
    Returns a string clean of html prefixes
    """
    clean_string = re.compile("<.*?>")
    summary = re.sub(clean_string, "", summary)
    return summary


# Function that extract two sentences from recipe's summary description
def extract_sentence(summary):
    """
    Returns first sentence of recipe's summary so that it can be displayed
    within the small item view
    """
    summary = clean_summary(summary)
    sentences = [sentence + "." for sentence in summary.split(".")]
    return sentences[0]


def parse_recipe_search_filter(filters, key):
    """
    Parses the search filters for recipe searching.
    """
    if key == "intolerances":
        if filters[key] is None:
            return (None, None)
        return (
            "intolerances",
            list_to_comma_separated_string(
                [intolerance.get_display_name() for intolerance in filters[key]]
            ),
        )
    elif key == "cuisines":
        if filters[key] is None:
            return (None, None)
        return (
            "cuisine",
            list_to_comma_separated_string([str(cuisine) for cuisine in filters[key]]),
        )
    elif key == "diets":
        if filters[key] is None:
            return (None, None)
        return (
            "diet",
            list_to_comma_separated_string([str(diet) for diet in filters[key]]),
        )
    elif key == "ingredients":
        if filters[key] is None:
            return (None, None)
        return (
            "includeIngredients",
            list_to_comma_separated_string([ingredient for ingredient in filters[key]]),
        )
    elif key == "max_prep_time":
        if filters[key] <= -1:
            return (None, None)
        return ("maxReadyTime", int(filters[key]))
    else:
        raise SpoonacularApiException(f'Invalid recipe search filter "{key}"')


def search_recipes(
    query: str,
    filters: dict = None,
    sort_by: SortCriteria = None,
    offset: int = 0,
    limit: int = 10,
) -> tuple(list[dict], int):
    """
    Returns a list of recipes which match the specified search query.

    Args:
        query (str): The search query to use.
        filters (dict): The search filters to use.
            This argument is an optional dictionary
            which contains one or more of the following mappings:
            intolerances (list[UserIntolerance]): The list of intolerances to use as a filter.
            cuisines (list[Cuisine]): The list of cuisines to use as a filter.
            diets (list[Diet]): The list of diets to use as a filter.
            ingredients (list[int]): The list of ingredient IDs to use as a filter.
            max_prep_time (int): The maximum prep time for the recipes (in minutes).
        sort_by (SortCriteria): The criteria to use to sort the results.
            This argument is optional.
        offset (int): The offset into the results to start at.
            This argument is optional and by default is 0.
        limit (int): The maximum number of results to return.
            This argument is optional and by default is 10.

    Returns:
        A tuple containing the list of recipes which match the provided search query,
        or an empty list if no recipes match the query,
        and an integer describing the maximum number of available results.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the search request.
    """
    params = {"apiKey": get_api_key()}

    for search_filter in filters.keys():
        (key, value) = parse_recipe_search_filter(filters, search_filter)
        if key is not None and value is not None:
            params[key] = value

    if sort_by is not None:
        params["sort"] = str(sort_by)

    params["offset"] = offset
    params["number"] = limit
    params["query"] = query

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + "recipes/complexSearch",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as exc:
        raise SpoonacularApiException("Failed to make recipe search request") from exc

    if data is None:
        raise SpoonacularApiException(
            "Failed to make recipe search request (malformed response)"
        )

    total_results = data["totalResults"]
    recipes = []

    try:
        for recipe in data["results"]:
            recipes.append(
                {"id": recipe["id"], "name": recipe["title"], "image": recipe["image"]}
            )
    except KeyError as exc:
        raise SpoonacularApiException("Malformed response") from exc

    return (recipes, total_results)


# pylint: disable=too-many-arguments
def search_recipes_old(
    ingredients: list[str],
    intolerances: list[Intolerance] = None,
    cuisines: list[Cuisine] = None,
    diets: list[Diet] = None,
    max_prep_time: int = -1,
    sort_by: SortCriteria = None,
    offset: int = 0,
    limit: int = 12,
) -> list:
    """
    Searches for recipes using the specified criteria and returns a list of JSON-encoded recipes.

    Args:
        ingredients (list[str]): A list of ingredients.
        intolerances (list[Intolerance]): A list of intolerances. This argument is optional.
        cuisines (list[Cuisine]): A list of cuisines. This argument is optional.
        diets (list[Diet]): A list of diets. This argument is optional.
        max_prep_time (int): The max amount of time it should take to prepare
            and cook the recipe. This argument is optional.
        sort_by (SortCriteria): The method to use to sort
            the returned recipes. This argument is optional.
        offset (int): The offset into the total amount of
            search results to start retrieving recipes.
            This argument is optional and by default is 0.
        limit (int): The maximum number of recipes to get.
            This argument is optional and by default is 10.

    Returns:
        A list of JSON-encoded recipes. If no recipes were found that
            matched the given criteria, this function will return an empty list.
        Each recipe object consists of the following values:
            - id (int): The ID of the recipe.
            - name (str): The display name of the recipe.
            - image (str): The URL of the image for the recipe.
            - summary (str): First sentence of summary content.
            - full_summary (str): Complete summary string for recipe.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the search request.
    """

    params = {"apiKey": get_api_key()}

    params["includeIngredients"] = list_to_comma_separated_string(ingredients)

    if intolerances is not None:
        params["intolerances"] = list_to_comma_separated_string(intolerances)

    if cuisines is not None:
        params["cuisine"] = list_to_comma_separated_string(cuisines)

    if diets is not None:
        params["diet"] = list_to_comma_separated_string(diets)

    if max_prep_time > -1:
        params["maxReadyTime"] = max_prep_time

    if sort_by is not None:
        params["sort"] = str(sort_by)

    params["offset"] = offset
    params["number"] = limit

    data = None

    # combines ingredients param to properly search the website
    #
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT
            + "recipes/complexSearch?query="
            + ingredients,
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(
            f"Failed to make recipe search request: {str(e)}"
        ) from e

    recipes = []
    for recipe in data["results"]:
        recipe_dict = {}
        try:
            recipe_dict["id"] = recipe["id"]
            recipe_dict["name"] = recipe["title"]
            # The following try/KeyError is meant to address issues regarding unavailable images
            # and summary during the API in case we still need to show content. This ensures the
            # found recipe is included instead of causing an empty return or dictionary keyerror
            # during html display
            try:
                recipe_dict["image"] = recipe["image"]
                summary = get_recipe_summary(recipe["id"])
                recipe_dict["summary"] = extract_sentence(summary)
                recipe_dict["full_summary"] = clean_summary(summary)
            except KeyError:
                recipe_dict["image"] = "../static/assets/noimage.jpg"
                recipe_dict[
                    "summary"
                ] = "Try this recipe to add variety into your diet!"
                recipe_dict[
                    "full_summary"
                ] = "Try this recipe to add variety into your diet!"
        except KeyError:
            print("Unable to extract recipe data")
        recipes.append(recipe_dict)

    return recipes


def get_recipe(recipe_id: int) -> Recipe:
    """
    Returns a `Recipe` object associated with the specified ID.

    Args:
        id (int) - The ID of the recipe to get.

    Returns:
        A recipe object which matches the specified ID, or `None` if no recipe matches.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the request.
    """

    params = {"apiKey": get_api_key()}

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + f"recipes/{recipe_id}/information",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}") from e

    if not data:
        return None

    return Recipe(data)


def get_recipe_as_json(recipe_id: int) -> list:
    """
    Returns a list of JSON-encoded data associated with the specified ID.

    Args:
        recipe_id (int) - The ID of the recipe to get.

    Returns:
        A list of JSON-encoded recipes. If no recipes were found that matched the given
        criteria, this function will return an empty list.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the request.
    """

    params = {"apiKey": get_api_key()}

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + f"recipes/{recipe_id}/information",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}") from e

    if not data:
        return None

    return data


def get_similar_recipes(recipe_id: int, limit: int = 10) -> list:
    """
    Returns a list of recipes similar to the recipe with the specified ID.

    Args:
        recipe_id (int): The ID of the recipe to get.
        limit (int): The maximum number of results to return.
            This argument is optional and is 10 by default.

    Returns:
        A list of JSON-encoded recipes. If no recipe was found that
            matches the specified ID, or there were no similar recipes found,
            this function will return an empty list.
        Each recipe object consists of the following values:
            - id (int): The ID of the recipe.
            - name (str): The display name of the recipe.
            - image (str): The URL of the image for the recipe.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the request.
    """

    params = {"apiKey": get_api_key(), "number": limit}

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + f"recipes/{recipe_id}/similar",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}") from e

    if not data:
        return None

    result = []
    for recipe in data:
        # We are using the get_recipe function because the similar_recipes endpoint
        # does not produce the full content that is available for each recipe
        extended_recipe = get_recipe_as_json(recipe["id"])
        recipe_dict = {}
        try:
            recipe_dict["id"] = extended_recipe["id"]
            recipe_dict["name"] = extended_recipe["title"]
            # The following try/KeyError is meant to address issues regarding unavailable images
            # and summary during the API in case we still need to show content. This ensures the
            # found recipe is included instead of causing an empty return or dictionary keyerror
            # during html display
            try:
                recipe_dict["image"] = extended_recipe["image"]
                summary = extended_recipe["summary"]
                recipe_dict["summary"] = extract_sentence(summary)
                recipe_dict["full_summary"] = clean_summary(summary)
            except KeyError:
                recipe_dict["image"] = "../static/assets/noimage.jpg"
                recipe_dict[
                    "summary"
                ] = "Try this recipe to add variety into your diet!"
                recipe_dict[
                    "full_summary"
                ] = "Try this recipe to add variety into your diet!"
        except KeyError:
            print("Error: Unable to retrieve recipe data")
        result.append(recipe_dict)

    return result


def get_recommended_recipes(
    offset: int = 0,
    limit: int = 12,
) -> list:
    """
    Returns a list of randomly recommended recipes.

    Args:
        "number" for representing the maximum amount of recipes

    Returns:
        A list of JSON-encoded recipes.
        Each recipe object consists of the following values:
            - id (int): The ID of the recipe.
            - name (str): The display name of the recipe.
            - image (str): The URL of the image for the recipe.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the request.
    """

    params = {"apiKey": get_api_key()}
    params["offset"] = offset
    params["number"] = limit

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + "recipes/random?",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}") from e

    if not data:
        return None

    result = []
    for recipe in data["recipes"]:
        recipe_dict = {}
        try:
            recipe_dict["id"] = recipe["id"]
            recipe_dict["name"] = recipe["title"]
            # The following try/KeyError is meant to address issues regarding unavailable images
            # and summary during the API in case we still need to show content. This ensures the
            # found recipe is included instead of causing an empty return or dictionary keyerror
            # during html display
            try:
                recipe_dict["image"] = recipe["image"]
                recipe_dict["full_summary"] = clean_summary(recipe["summary"])
                recipe_dict["summary"] = extract_sentence(recipe["summary"])
            except KeyError:
                recipe_dict["image"] = "../static/assets/noimage.jpg"
                recipe_dict[
                    "full_summary"
                ] = "Add some variety to you diet by trying this recipe!"
                recipe_dict[
                    "summary"
                ] = "Add some variety to you diet by trying this recipe!"
        except KeyError:
            print("Error: Unable to retrieve recipe data")

        result.append(recipe_dict)

    return result


def get_recipe_summary(recipe_id: int) -> str:
    """
    Returns a `Recipe's summary as an object associated with the specified ID.

    Args:
        id (int) - The ID of the recipe to get a summary for.

    Returns:
        A string object as a full summary which matches the specified ID,
            or `None` if no recipe matches.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the request.
    """

    params = {"apiKey": get_api_key()}

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + f"recipes/{recipe_id}/summary",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}") from e

    if not data:
        return None

    return data["summary"]


def parse_ingredient_search_filter(filters, key):
    """
    Parses the provided ingredient search filter.
    """
    if key == "intolerances":
        if filters[key] is None:
            return (None, None)
        return (
            "intolerances",
            list_to_comma_separated_string(
                [intolerance.get_display_name() for intolerance in filters[key]]
            ),
        )
    else:
        raise SpoonacularApiException(f'Invalid ingredient search filter "{key}"')


def search_ingredients(
    query: str,
    filters: dict = None,
    sort_by: SortCriteria = None,
    offset: int = 0,
    limit: int = 10,
) -> tuple[list[dict], int]:
    """
    Searches for ingredients using the specified criteria
        and returns a list of JSON-encoded recipes.

    Args:
        query (str): The search query to use to search for ingredients.
        filters (dict): A dictionary of search filters.
            This can contain one or more of the following values:
            intolerances (list[UserIntolerance]): A list of intolerances.
        sort_by (SortCriteria): The method to use to sort the
            returned ingredients. This argument is optional.
        offset (int): The offset into the total amount of search results to start
            retrieving ingredients. This argument is optional and by default is 0.
        limit (int): The maximum number of ingredients to get.
            This argument is optional and by default is 10.

    Returns:
        A list of JSON-encoded ingredients. If no ingredients were
            found that matched the given criteria, this function will return an empty list.
        Each ingredient object consists of the following values:
            - id (int): The ID of the ingredient.
            - name (str): The display name of the ingredient.
            - image (str): The URL of the image for the ingredient.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the search request.
    """
    params = {"apiKey": get_api_key()}

    for search_filter in filters.keys():
        (key, value) = parse_ingredient_search_filter(filters, search_filter)
        if key is not None and value is not None:
            params[key] = value

    if sort_by is not None:
        params["sort"] = str(sort_by)

    params["offset"] = offset
    params["number"] = limit
    params["query"] = query

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + "food/ingredients/search",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as exc:
        raise SpoonacularApiException(
            "Failed to make ingredient search request"
        ) from exc

    if data is None:
        raise SpoonacularApiException(
            "Failed to make ingredient search request (malformed response)"
        )

    total_results = data["totalResults"]
    ingredients = []

    image_url_prefix = "https://spoonacular.com/cdn/ingredients_500x500/"

    for ingredient in data["results"]:
        ingredients.append(
            {
                "id": ingredient["id"],
                "name": ingredient["title"],
                "image": image_url_prefix + str(ingredient["image"]),
            }
        )

    return (ingredients, total_results)


def search_ingredients_old(
    query: str,
    intolerances: list[Intolerance] = None,
    sort_by: SortCriteria = None,
    offset: int = 0,
    limit: int = 12,
) -> list:
    """
    Searches for ingredients using the specified criteria
        and returns a list of JSON-encoded recipes.

    Args:
        query (str): The search query to use to search for ingredients.
        intolerances (list[Intolerance]): A list of intolerances. This argument is optional.
        sort_by (SortCriteria): The method to use to sort the
            returned ingredients. This argument is optional.
        offset (int): The offset into the total amount of search results to start
            retrieving ingredients. This argument is optional and by default is 0.
        limit (int): The maximum number of ingredients to get.
            This argument is optional and by default is 10.

    Returns:
        A list of JSON-encoded ingredients. If no ingredients were
            found that matched the given criteria, this function will return an empty list.
        Each ingredient object consists of the following values:
            - id (int): The ID of the ingredient.
            - name (str): The display name of the ingredient.
            - image (str): The URL of the image for the ingredient.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the search request.
    """

    params = {"apiKey": get_api_key()}

    params["query"] = query

    if intolerances is not None:
        params["intolerances"] = list_to_comma_separated_string(intolerances)

    if sort_by is not None:
        params["sort"] = str(sort_by)

    params["offset"] = offset
    params["number"] = limit

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + "food/ingredients/search",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(
            f"Failed to make ingredient request: {str(e)}"
        ) from e
    # ingredients = data
    ingredients = []
    image_url = "https://spoonacular.com/cdn/ingredients_250x250/"
    for ingredient in data["results"]:
        ingredients.append(
            {
                "id": ingredient["id"],
                "name": ingredient["name"],
                "image": image_url + ingredient["image"],
            }
        )

    return ingredients


def get_ingredient(ingredient_id: int) -> Ingredient:
    """
    Returns an `Ingredient` object associated with the specified ID.

    Args:
        ingredient_id (int) - The ID of the ingredient to get.

    Returns:
        An ingredient object which matches the specified ID, or `None` if no ingredient matches.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the request.
    """

    params = {"apiKey": get_api_key()}

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT
            + f"food/ingredients/{ingredient_id}/information",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(
            f"Failed to make ingredient request: {str(e)}"
        ) from e

    if not data:
        return None

    return Ingredient(data)


def get_random_recipes(limit: int = 10):
    """
    Returns a random list of recipes.
    """

    params = {"apiKey": get_api_key()}

    if limit > 0:
        params["number"] = limit

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + "recipes/random",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as exc:
        raise SpoonacularApiException("Failed to make recipe request") from exc

    if data is None:
        raise SpoonacularApiException("Malformed response")

    try:
        result = []

        for recipe in data["recipes"]:
            result.append(
                {"id": recipe["id"], "name": recipe["title"], "image": recipe["image"]}
            )

        return result
    except KeyError as exc:
        raise SpoonacularApiException("Malformed response") from exc


def get_recipes_by_ingredients(ingredients: list[str], limit: int):
    """
    Returns a list of random recipes which include (up to) all of the specified ingredients.
    """
    params = {
        "apiKey": get_api_key(),
        "ingredients": list_to_comma_separated_string(ingredients),
    }

    if limit > 0:
        params["number"] = limit

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + "recipes/findByIngredients",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as exc:
        raise SpoonacularApiException("Failed to make recipe request") from exc

    if data is None:
        raise SpoonacularApiException("Malformed response")

    try:
        result = []

        for recipe in data:
            result.append(
                {"id": recipe["id"], "name": recipe["title"], "image": recipe["image"]}
            )

        return result
    except KeyError as exc:
        raise SpoonacularApiException("Malformed response") from exc
