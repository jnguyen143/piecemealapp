"""
This file tests the functionality of `database.Database.get_recommended_user_recipes()`.

Given a dummy user with dummy saved recipes, this file tests to make sure that
`get_recommended_user_recipes()` returns only the most recently liked recipes.

This file tests `get_recommended_user_recipes()` with randomly generated dummy
user data to ensure that it is robust enough to handle any kind of input data.
"""

import unittest
from unittest.mock import patch
from random import seed, randint
from .... import app


INPUT = "input"
EXPECTED_OUTPUT = "expected"


def generate_prefixed_string(prefix):
    """
    Generates a random string prefixed with the specified string.
    """
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


# pylint: disable=too-few-public-methods
# This is a POD class.
class MockedSavedRecipe:
    """
    Represents a saved ingredient.
    """

    def __init__(self, recipe_id, name, image):
        self.id = recipe_id
        self.name = name
        self.image = image

    def __repr__(self):
        return f"id={self.id}, name={self.name}, image={self.image}"


def generate_saved_recipe():
    """
    Returns a randomly generated recipe.
    """
    recipe_id = randint(0, 100000)
    name = generate_prefixed_string("saved_recipe_")
    image = generate_prefixed_string("image_")
    return MockedSavedRecipe(recipe_id, name, image)


def get_saved_recipes_mock(seedval):
    """
    Return a list of recipe objects, which amounts to a dict of id, name, and image
    Return between 0 and 100 recipes
    """
    seed(seedval)
    result = []
    for _ in range(0, randint(0, 100)):
        result.append(generate_saved_recipe())
    return result


def get_user_id_mock(seedval):
    """
    Returns a randomly generated user ID.
    """
    seed(seedval)
    return generate_prefixed_string("user_")


def get_limit_mock(seedval):
    """
    Returns a randomly generated limit.
    """
    seed(seedval)
    return randint(1, 10)


def get_expected_output(seedval):
    """
    Returns the expected output for the test.
    """
    saved_recipes = get_saved_recipes_mock(seedval)
    limit = get_limit_mock(seedval)
    return saved_recipes[-limit:]


def recipes_match(recipe_a, recipe_b):
    """
    Returns true if the two recipes match.
    """
    try:
        return (
            recipe_a.id == recipe_b.id
            and recipe_a.name == recipe_b.name
            and recipe_a.image == recipe_b.image
        )
    except KeyError:
        return False


def contains_recipe(src, target):
    """
    Returns true if the source contains the target recipe.
    """
    for recipe in src:
        if recipes_match(recipe, target):
            return True
    return False


def validate_input(recipes, expected_output):
    """
    Returns true if the provided output matches the expected output.
    """
    for recipe in recipes:
        if not contains_recipe(expected_output, recipe):
            return False
    return True


class GetRecommendedUserRecipesTestCase(unittest.TestCase):
    """
    The class that holds the actual test.
    """

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def setUp(self):
        """
        Sets up the test.
        """
        self.test_success_params = []
        for _ in range(0, 10):
            seedval = randint(0, 100)
            self.test_success_params.append(
                {
                    INPUT: {
                        "seedval": seedval,
                        "saved_recipes": get_saved_recipes_mock(seedval),
                        "user_id": get_user_id_mock(seedval),
                        "limit": get_limit_mock(seedval),
                    },
                    EXPECTED_OUTPUT: get_expected_output(seedval),
                }
            )

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def runTest(self):
        """
        Runs the test.
        """
        app.init_app()
        for test in self.test_success_params:
            with patch(
                "app.database.database.Database.get_recipes"
            ) as db_get_saved_recipes:
                db_get_saved_recipes.return_value = (test[INPUT]["saved_recipes"], 0)
                validation = validate_input(
                    app.DATABASE.get_user_top_recipes(
                        test[INPUT]["user_id"], test[INPUT]["limit"]
                    ),
                    test[EXPECTED_OUTPUT],
                )
                self.assertTrue(
                    validation,
                    f"Assertion failed for input with seed {test[INPUT]['seedval']}",
                )


if __name__ == "__main__":
    unittest.main()
