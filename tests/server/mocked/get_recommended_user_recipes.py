"""
This file tests the functionality of `database.Database.get_recommended_user_recipes()`.

Given a dummy user with dummy saved recipes, this file tests to make sure that `get_recommended_user_recipes()` returns only the most recently liked recipes.

This file tests `get_recommended_user_recipes()` with randomly generated dummy user data to ensure that it is robust enough to handle any kind of input data.
"""

import unittest
from unittest.mock import patch
from random import seed, randint


def init_app_module_dir():
    import sys
    import pathlib

    path = str(
        pathlib.Path(__file__).parent.parent.parent.parent.joinpath("src").resolve()
    )
    sys.path.append(path)


INPUT = "input"
EXPECTED_OUTPUT = "expected"


def generate_prefixed_string(prefix):
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


class MockedSavedRecipe:
    def __init__(self, id, name, image):
        self.id = id
        self.name = name
        self.image = image

    def __repr__(self):
        return f"id={self.id}, name={self.name}, image={self.image}"


def generate_saved_recipe():
    id = randint(0, 100000)
    name = generate_prefixed_string("saved_recipe_")
    image = generate_prefixed_string("image_")
    return MockedSavedRecipe(id, name, image)


def get_saved_recipes_mock(seedval):
    # Return a list of recipe objects, which amounts to a dict of id, name, and image
    # Return between 0 and 100 recipes
    seed(seedval)
    result = []
    for _ in range(0, randint(0, 100)):
        result.append(generate_saved_recipe())
    return result


def get_user_id_mock(seedval):
    seed(seedval)
    return generate_prefixed_string("user_")


def get_limit_mock(seedval):
    seed(seedval)
    return randint(1, 10)


def get_expected_output(seedval):
    saved_recipes = get_saved_recipes_mock(seedval)
    limit = get_limit_mock(seedval)
    return saved_recipes[-limit:]


def recipes_match(a, b):
    try:
        return a.id == b.id and a.name == b.name and a.image == b.image
    except:
        return False


def contains_recipe(src, target):
    for recipe in src:
        if recipes_match(recipe, target):
            return True
    return False


def validate_input(recipes, expected_output):
    for recipe in recipes:
        if not contains_recipe(expected_output, recipe):
            return False
    return True


class GetRecommendedUserRecipesTestCase(unittest.TestCase):
    def setUp(self):
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

    def runTest(self):
        init_app_module_dir()
        # If the below comment is not present, pylance will generate an import warning. We know the import is valid because the above function call injects the required module directory.
        import app  # pyright: reportMissingImports=false

        app.init_app()
        for test in self.test_success_params:
            with patch(
                "database.database.Database.get_saved_recipes"
            ) as db_get_saved_recipes:
                db_get_saved_recipes.return_value = test[INPUT]["saved_recipes"]
                validation = validate_input(
                    app.db.get_recommended_recipes_from_user(
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
