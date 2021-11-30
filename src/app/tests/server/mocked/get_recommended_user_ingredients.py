"""
This file tests the functionality of `database.Database.get_recommended_user_ingredients()`.
Given a dummy user with dummy saved ingredients, this file tests to make sure that
 `get_recommended_user_ingredients()` returns only the most recently liked ingredients.
This file tests the `get_recommended_user_ingredients()' function with random dummy
user data to ensure that it can handle any kind of input data.
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
class MockedSavedingredient:
    """
    Represents a saved ingredient.
    """

    def __init__(self, ingredient_id, name, image):
        self.id = ingredient_id
        self.name = name
        self.image = image

    def __repr__(self):
        return f"id={self.id}, name={self.name}, image={self.image}"


def generate_saved_ingredient():
    """
    Generates a random saved ingredient.
    """
    ingredient_id = randint(0, 100000)
    name = generate_prefixed_string("saved_ingredient_")
    image = generate_prefixed_string("image_")
    return MockedSavedingredient(ingredient_id, name, image)


def get_saved_ingredients_mock(seedval):
    """
    Return a list of ingredient objects, which amounts to a dict of ingredient_id, name, and image
    Return between 0 and 100 ingredients
    """
    seed(seedval)
    result = []
    for _ in range(0, randint(0, 100)):
        result.append(generate_saved_ingredient())
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
    Returns the expected output.
    """
    saved_ingredients = get_saved_ingredients_mock(seedval)
    limit = get_limit_mock(seedval)
    return saved_ingredients[-limit:]


def ingredients_match(ingredient_a, ingredient_b):
    """
    Returns true if the two ingredients match.
    """
    try:
        return (
            ingredient_a.id == ingredient_b.id
            and ingredient_a.name == ingredient_b.name
            and ingredient_a.image == ingredient_b.image
        )
    except KeyError:
        return False


def contains_ingredient(src, target):
    """
    Returns true if the source contains the target ingredient.
    """
    for ingredient in src:
        if ingredients_match(ingredient, target):
            return True
    return False


def validate_input(ingredients, expected_output):
    """
    Returns true if the provided output matches the expected output.
    """
    for ingredient in ingredients:
        if not contains_ingredient(expected_output, ingredient):
            return False
    return True


class GetRecommendedUserIngredientsTestCase(unittest.TestCase):
    """
    Holds the actual test case.
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
                        "saved_ingredients": get_saved_ingredients_mock(seedval),
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
                "app.database.database.Database.get_ingredients"
            ) as db_get_saved_ingredients:
                db_get_saved_ingredients.return_value = (
                    test[INPUT]["saved_ingredients"],
                    0,
                )
                validation = validate_input(
                    app.DATABASE.get_user_top_ingredients(
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
