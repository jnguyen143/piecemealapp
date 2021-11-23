# pylint: disable=(C0114)
# pylint: disable=(E0401)
import unittest
from unittest.mock import patch
from random import seed, randint
import sys
import pathlib


# pylint: disable=(W0105)
# disabled error for string
# comment below
# being declared as useless
"""
This file tests the functionality of `database.Database.get_recommended_user_ingredients()`.
Given a dummy user with dummy saved ingredients, this file tests to make sure that
 `get_recommended_user_ingredients()` returns only the most recently liked ingredients.
This file tests the `get_recommended_user_ingredients()' function with random dummy
user data to ensure that it can handle any kind of input data.
"""

# pylint: disable=(C0116)
def init_app_module_dir():

    path = str(
        pathlib.Path(__file__).parent.parent.parent.parent.joinpath("src").resolve()
    )
    sys.path.append(path)


INPUT = "input"
EXPECTED_OUTPUT = "expected"

# pylint: disable=(C0116)
def generate_prefixed_string(prefix):
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


# pylint: disable=(C0115)
class MockedSavedingredient:
    # pylint: disable=(W0622)
    # disabled built in error
    def __init__(self, id, name, image):
        # pylint: disable=(C0103)
        # disabled snake case error
        self.id = id
        self.name = name
        self.image = image

    # pylint: disable=(C0116)
    def __repr__(self):
        return f"id={self.id}, name={self.name}, image={self.image}"


# pylint: disable=(C0116)
def generate_saved_ingredient():
    # pylint: disable=(W0622)
    # disabled built in error
    # pylint: disable=(C0103)
    # disabled snake case error
    id = randint(0, 100000)
    name = generate_prefixed_string("saved_ingredient_")
    image = generate_prefixed_string("image_")
    return MockedSavedingredient(id, name, image)


# pylint: disable=(C0116)
def get_saved_ingredients_mock(seedval):
    # Return a list of ingredient objects, which amounts to a dict of id, name, and image
    # Return between 0 and 100 ingredients
    seed(seedval)
    result = []
    for _ in range(0, randint(0, 100)):
        result.append(generate_saved_ingredient())
    return result


# pylint: disable=(C0116)
def get_user_id_mock(seedval):
    seed(seedval)
    return generate_prefixed_string("user_")


# pylint: disable=(C0116)
def get_limit_mock(seedval):
    seed(seedval)
    return randint(1, 10)


# pylint: disable=(C0116)
def get_expected_output(seedval):
    saved_ingredients = get_saved_ingredients_mock(seedval)
    limit = get_limit_mock(seedval)
    return saved_ingredients[-limit:]


# pylint: disable=(C0103)
# disabled snake case error
def ingredients_match(a, b):

    try:
        return a.id == b.id and a.name == b.name and a.image == b.image
    # pylint: disable=(W0702)
    # disabled except error
    except:
        return False


def contains_ingredient(src, target):
    for ingredient in src:
        if ingredients_match(ingredient, target):
            return True
    return False


# pylint: disable=(C0115)


def validate_input(ingredients, expected_output):
    for ingredient in ingredients:
        if not contains_ingredient(expected_output, ingredient):
            return False
    return True


class GetRecommendedUserIngredientsTestCase(unittest.TestCase):
    def setUp(self):
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

    def runTest(self):

        init_app_module_dir()
        # pylint: disable=import-outside-toplevel
        # This import must occur after the above function runs.
        import app

        # If the below comment is not present, pylance will generate
        # an import warning. We know the import is valid because the
        #  above function call injects the required module directory.
        # pyright: reportMissingImports=false

        app.init_app()
        for test in self.test_success_params:
            with patch(
                "database.database.Database.get_saved_ingredients"
            ) as db_get_saved_ingredients:
                db_get_saved_ingredients.return_value = test[INPUT]["saved_ingredients"]
                validation = validate_input(
                    app.db.get_recommended_ingredients_from_user(
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
