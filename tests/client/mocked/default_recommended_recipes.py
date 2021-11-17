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
This file tests the correctness of default
recommended recipes being rendered to the homepage.

Given a set of dummy default recommended recipes,
this file ensures that the recipes are being
rendered to the generated HTML page returned by the '/' endpoint.
"""

# pylint: disable=(C0116)
def init_app_module_dir():

    path = str(
        pathlib.Path(__file__).parent.parent.parent.parent.joinpath("src").resolve()
    )
    sys.path.append(path)


INPUT = "input"

# pylint: disable=(C0116)
def generate_prefixed_string(prefix):
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


# pylint: disable=(C0116)
def validate_page(recipes, page: str):
    for recipe in recipes:
        if page.find(recipe["name"]) == -1:
            return False
        if page.find(recipe["image"]) == -1:
            return False
        if page.find(recipe["summary"]) == -1:
            return False
    return True


def generate_recipe():
    # pylint: disable=(W0622)
    # disabled redefined built in error
    # pylint: disable=(C0103)
    # disabled snake case error
    id = generate_prefixed_string("id_")
    name = generate_prefixed_string("name_")
    image = generate_prefixed_string("image_")
    full_summary = generate_prefixed_string("full_summary_")
    summary = generate_prefixed_string("summary_")
    return {
        "id": id,
        "name": name,
        "image": image,
        "full_summary": full_summary,
        "summary": summary,
    }


# pylint: disable=(C0116)
def generate_recommended_recipes(seedval):
    seed(seedval)
    result = []
    for _ in range(0, randint(0, 10)):
        result.append(generate_recipe())
    return result


# pylint: disable=(C0115)
class DefaultRecommendedRecipesTest(unittest.TestCase):
    # pylint: disable=(C0116)
    def setUp(self):
        self.test_success_params = []
        for _ in range(0, 10):
            seedval = randint(0, 100)
            self.test_success_params.append(
                {
                    INPUT: {
                        "seedval": seedval,
                        "recommended_recipes": generate_recommended_recipes(seedval),
                    }
                }
            )

    # pylint: disable=(C0103)
    # disabled  snake case error
    def runTest(self):

        init_app_module_dir()
        import app

        # If the below comment is not present,
        # pylance will generate an import warning.
        # We know the import is valid because the
        # above function call injects the required module directory.
        # pyright: reportMissingImports=false

        app.init_app()
        from routes import index

        for test in self.test_success_params:
            with patch("routes.index.get_current_user") as index_get_current_user:
                with patch(
                    "routes.index.get_recommended_recipes_from_spoonacular"
                ) as get_recommended_recipes_from_spoonacular:
                    # Mock out the values
                    index_get_current_user.return_value = None
                    get_recommended_recipes_from_spoonacular.return_value = test[INPUT][
                        "recommended_recipes"
                    ]

                    # Render page
                    page_content = ""
                    with app.get_app().app_context():
                        page_content: str = index.index()

                    # Validate page
                    result = validate_page(
                        test[INPUT]["recommended_recipes"], page_content
                    )
                    self.assertTrue(
                        result,
                        f"Assertion failed for input with seed {test[INPUT]['seedval']}",
                    )


if __name__ == "__main__":
    unittest.main()
