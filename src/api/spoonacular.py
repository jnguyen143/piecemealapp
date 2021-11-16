"""
==================== SPOONACULAR API ====================
This file defines the functions necessary to communicate with the Spoonacular API.
Before any of the functions in this file can be called, 
you must ensure that the `SPOONACULAR_API_KEY` environment variable has been defined.
"""

from api.common import (
    api_get_json,
    RequestException,
    MalformedResponseException,
    UndefinedApiKeyException,
)
from enum import Enum
from os import getenv
import re


class SpoonacularApiException(Exception):
    """
    Raised if there is a problem making a Spoonacular API call.
    """

    def __init__(self, message=""):
        self.message = message


class Intolerance(Enum):
    """
    The available intolerances that can be fed to the Spoonacular API calls, such as for `search_recipes()`.
    """

    Dairy = "Dairy"
    Egg = "Egg"
    Gluten = "Gluten"
    Grain = "Grain"
    Peanut = "Peanut"
    Seafood = "Seafood"
    Sesame = "Sesame"
    Shellfish = "Shellfish"
    Soy = "Soy"
    Sulfite = "Sulfite"
    TreeNut = "Tree Nut"
    Wheat = "Wheat"

    @classmethod
    def has(cls, value):
        return value in cls._value2member_map_


class Cuisine(Enum):
    """
    The available cuisines that can be fed to the Spoonacular API calls, such as for `search_recipes()`.
    """

    African = "African"
    American = "American"
    British = "British"
    Cajun = "Cajun"
    Caribbean = "Caribbean"
    Chinese = "Chinese"
    EasternEuropean = "Eastern European"
    European = "European"
    French = "French"
    German = "German"
    Greek = "Greek"
    Indian = "Indian"
    Irish = "Irish"
    Italian = "Italian"
    Japanese = "Japanese"
    Jewish = "Jewish"
    Korean = "Korean"
    LatinAmerican = "Latin American"
    Mediterranean = "Mediterranean"
    Mexican = "Mexican"
    MiddleEastern = "Middle Eastern"
    Nordic = "Nordic"
    Southern = "Southern"
    Spanish = "Spanish"
    Thai = "Thai"
    Vietnamese = "Vietnamese"


class Diet(Enum):
    """
    The available diets that can be fed to the Spoonacular API calls, such as for `search_recipes()`.
    """

    GlutenFree = "Gluten Free"
    Ketogenic = "Ketogenic"
    Vegetarian = "Vegetarian"
    LactoVegetarian = "Lacto-Vegetarian"
    OvoVegetarian = "Ovo-Vegetarian"
    Vegan = "Vegan"
    Pescetarian = "Pescetarian"
    Paleo = "Paleo"
    Primal = "Primal"
    LowFodmap = "Low FODMAP"
    Whole30 = "Whole30"


class SortCriteria(Enum):
    """
    The available criteria used to sort the results returned by `search_recipes()`.
    """

    Popularity = "popularity"
    Healthiness = "healthiness"
    Price = "price"
    Time = "time"
    Random = "random"
    MaxUsedIngredients = "max-used-ingredients"
    MinMissingIngredients = "min-missing-ingredients"
    Calories = "calories"
    Carbohydrates = "carbohydrates"
    TotalFat = "total-fat"
    Protein = "protein"
    Sugar = "sugar"
    Sodium = "sodium"


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

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["title"]
        self.image = kwargs["image"]
        self.prep_time = kwargs["readyInMinutes"]
        self.servings = kwargs["servings"]
        self.source_url = kwargs("sourceUrl")
        self.cuisines = [Cuisine(x) for x in kwargs["cuisines"]]
        self.diets = [Diet(x) for x in kwargs["diets"]]
        self.gluten_free = kwargs["gluten_free"]
        self.ketogenic = kwargs["ketogenic"]
        self.low_fodmap = kwargs["lowFodmap"]
        self.vegan = kwargs["vegan"]
        self.vegetarian = kwargs["vegetarian"]
        self.whole30 = kwargs["whole30"]
        self.healthy = kwargs["veryHealthy"]
        self.popular = kwargs["veryPopular"]
        self.summary = kwargs["summary"]

        ingredients = []
        for x in kwargs["extendedIngredients"]:
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

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["title"]
        self.image = kwargs["image"]
        for x in kwargs["nutrition"]["nutrients"]:
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

    if key == None:
        raise UndefinedApiKeyException("Undefined Spoonacular API key")

    return key


def list_to_comma_separated_string(lst: list) -> str:
    """
    Returns the list of objects as a comma-separated string.
    If the list is empty, this function will return an empty string.
    """
    result = ""
    for i in range(0, len(lst)):
        if i > 0:
            result += ","
        result += str(lst[i])
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


def search_recipes(
    ingredients: list[str],
    intolerances: list[Intolerance] = None,
    cuisines: list[Cuisine] = None,
    diets: list[Diet] = None,
    max_prep_time: int = -1,
    sort_by: SortCriteria = None,
    offset: int = 0,
    limit: int = 10,
) -> list:
    """
    Searches for recipes using the specified criteria and returns a list of JSON-encoded recipes.

    Args:
        ingredients (list[str]): A list of ingredients.
        intolerances (list[Intolerance]): A list of intolerances. This argument is optional.
        cuisines (list[Cuisine]): A list of cuisines. This argument is optional.
        diets (list[Diet]): A list of diets. This argument is optional.
        max_prep_time (int): The max amount of time it should take to prepare and cook the recipe. This argument is optional.
        sort_by (SortCriteria): The method to use to sort the returned recipes. This argument is optional.
        offset (int): The offset into the total amount of search results to start retrieving recipes. This argument is optional and by default is 0.
        limit (int): The maximum number of recipes to get. This argument is optional and by default is 10.

    Returns:
        A list of JSON-encoded recipes. If no recipes were found that matched the given criteria, this function will return an empty list.
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

    if intolerances != None:
        params["intolerances"] = list_to_comma_separated_string(intolerances)

    if cuisines != None:
        params["cuisine"] = list_to_comma_separated_string(cuisines)

    if diets != None:
        params["diet"] = list_to_comma_separated_string(diets)

    if max_prep_time > -1:
        params["maxReadyTime"] = max_prep_time

    if sort_by != None:
        params["sort"] = str(sort_by)

    params["offset"] = offset
    params["number"] = limit

    data = None

    # combines ingredients param to properly search the website
    #
    URL = "recipes/complexSearch?query=" + ingredients
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + URL,
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe search request: {str(e)}")

    recipes = []
    for recipe in data["results"]:
        dict = {}
        try:
            dict["id"] = recipe["id"]
            dict["name"] = recipe["title"]
            """
            The following try/KeyError is meant to address issues regarding unavailable images 
            and summary during the API in case we still need to show content. This ensures the 
            found recipe is included instead of causing an empty return or dictionary keyerror
            during html display
            """
            try:
                dict["image"] = recipe["image"]
                summary = get_recipe_summary(recipe["id"])
                dict["summary"] = extract_sentence(summary)
                dict["full_summary"] = clean_summary(summary)
            except KeyError:
                dict["image"] = "../static/assets/noimage.jpg"
                dict["summary"] = "Try this recipe to add variety into your diet!"
                dict["full_summary"] = "Try this recipe to add variety into your diet!"
        except KeyError:
            print("Unable to extract recipe data")
        recipes.append(dict)

    return recipes


def get_recipe(id: int) -> Recipe:
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
            SPOONACULAR_API_ROOT_ENDPOINT + f"recipes/{id}/information",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}")

    if not data:
        return None

    return Recipe(data)


def get_recipe_as_json(id: int) -> list:
    """
    Returns a list of JSON-encoded data associated with the specified ID.

    Args:
        id (int) - The ID of the recipe to get.

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
            SPOONACULAR_API_ROOT_ENDPOINT + f"recipes/{id}/information",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}")

    if not data:
        return None

    return data


def get_similar_recipes(id: int) -> list:
    """
    Returns a list of recipes similar to the recipe with the specified ID.

    Args:
        id (int) - The ID of the recipe to get.

    Returns:
        A list of JSON-encoded recipes. If no recipe was found that matches the specified ID, or there were no similar recipes found, this function will return an empty list.
        Each recipe object consists of the following values:
            - id (int): The ID of the recipe.
            - name (str): The display name of the recipe.
            - image (str): The URL of the image for the recipe.

    Raises:
        UndefinedApiKeyException: If the Spoonacular API key is undefined.
        SpoonacularApiException: If there was a problem completing the request.
    """

    params = {"apiKey": get_api_key()}

    data = None
    try:
        data = api_get_json(
            SPOONACULAR_API_ROOT_ENDPOINT + f"recipes/{id}/similar",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}")

    if not data:
        return None

    result = []
    for recipe in data:
        # We are using the get_recipe function because the similar_recipes endpoint
        # does not produce the full content that is available for each recipe
        extended_recipe = get_recipe_as_json(recipe["id"])
        dict = {}
        try:
            dict["id"] = extended_recipe["id"]
            dict["name"] = extended_recipe["title"]
            """
            The following try/KeyError is meant to address issues regarding unavailable images 
            and summary during the API in case we still need to show content. This ensures the 
            found recipe is included instead of causing an empty return or dictionary keyerror
            during html display
            """
            try:
                dict["image"] = extended_recipe["image"]
                summary = extended_recipe["summary"]
                dict["summary"] = extract_sentence(summary)
                dict["full_summary"] = clean_summary(summary)
            except KeyError:
                dict["image"] = "../static/assets/noimage.jpg"
                dict["summary"] = "Try this recipe to add variety into your diet!"
                dict["full_summary"] = "Try this recipe to add variety into your diet!"
        except KeyError:
            print("Error: Unable to retrieve recipe data")
        result.append(dict)

    return result


def get_recommended_recipes(
    offset: int = 0,
    limit: int = 10,
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
            SPOONACULAR_API_ROOT_ENDPOINT + f"recipes/random?",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}")

    if not data:
        return None

    result = []
    for recipe in data["recipes"]:
        dict = {}
        try:
            dict["id"] = recipe["id"]
            dict["name"] = recipe["title"]
            """
            The following try/KeyError is meant to address issues regarding unavailable images 
            and summary during the API in case we still need to show content. This ensures the 
            found recipe is included instead of causing an empty return or dictionary keyerror
            during html display
            """
            try:
                dict["image"] = recipe["image"]
                dict["full_summary"] = clean_summary(recipe["summary"])
                dict["summary"] = extract_sentence(recipe["summary"])
            except KeyError:
                dict["image"] = "../static/assets/noimage.jpg"
                dict[
                    "full_summary"
                ] = "Add some variety to you diet by trying this recipe!"
                dict["summary"] = "Add some variety to you diet by trying this recipe!"
        except KeyError:
            print("Error: Unable to retrieve recipe data")

        result.append(dict)

    return result


def get_recipe_summary(recipe_id: int) -> str:
    """
    Returns a `Recipe's summary as an object associated with the specified ID.

    Args:
        id (int) - The ID of the recipe to get a summary for.

    Returns:
        A string object as a full summary which matches the specified ID, or `None` if no recipe matches.

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
        raise SpoonacularApiException(f"Failed to make recipe request: {str(e)}")

    if not data:
        return None

    return data["summary"]


def search_ingredients(
    query: str,
    intolerances: list[Intolerance] = None,
    sort_by: SortCriteria = None,
    offset: int = 0,
    limit: int = 10,
) -> list:
    """
    Searches for ingredients using the specified criteria and returns a list of JSON-encoded recipes.

    Args:
        query (str): The search query to use to search for ingredients.
        intolerances (list[Intolerance]): A list of intolerances. This argument is optional.
        sort_by (SortCriteria): The method to use to sort the returned ingredients. This argument is optional.
        offset (int): The offset into the total amount of search results to start retrieving ingredients. This argument is optional and by default is 0.
        limit (int): The maximum number of ingredients to get. This argument is optional and by default is 10.

    Returns:
        A list of JSON-encoded ingredients. If no ingredients were found that matched the given criteria, this function will return an empty list.
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

    if intolerances != None:
        params["intolerances"] = list_to_comma_separated_string(intolerances)

    if sort_by != None:
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
        raise SpoonacularApiException(f"Failed to make ingredient request: {str(e)}")
    # ingredients = data
    ingredients = []
    imageURL = "https://spoonacular.com/cdn/ingredients_250x250/"
    for ingredient in data["results"]:
        ingredients.append(
            {
                "id": ingredient["id"],
                "name": ingredient["name"],
                "image": imageURL + ingredient["image"],
            }
        )

    return ingredients


def get_ingredient(id: int) -> Ingredient:
    """
    Returns an `Ingredient` object associated with the specified ID.

    Args:
        id (int) - The ID of the ingredient to get.

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
            SPOONACULAR_API_ROOT_ENDPOINT + f"food/ingredients/{id}/information",
            headers={"Content-Type": "application/json"},
            params=params,
        )
    except (RequestException, MalformedResponseException) as e:
        raise SpoonacularApiException(f"Failed to make ingredient request: {str(e)}")

    if not data:
        return None

    return Ingredient(data)
