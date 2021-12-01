"""
This file tests the correctness of default
recommended recipes being rendered to the homepage.

Given a set of dummy default recommended recipes,
this file ensures that the recipes are being
rendered to the generated HTML page returned by the '/' endpoint.
"""

import unittest
from unittest.mock import patch
from random import seed, randint
from .... import app
from ....routes.html import index

INPUT = "input"


def generate_prefixed_string(prefix):
    """
    Generates a random string prefixed with the specified string.
    """
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


def validate_page(recipes, page: str):
    """
    Validates the index page.
    """
    for recipe in recipes:
        if page.find(recipe["name"]) == -1:
            return False
        if page.find(recipe["image"]) == -1:
            return False
        if page.find(recipe["summary"]) == -1:
            return False
    return True


def generate_recipe():
    """
    Generates a random recipe.
    """
    recipe_id = generate_prefixed_string("id_")
    name = generate_prefixed_string("name_")
    image = generate_prefixed_string("image_")
    full_summary = generate_prefixed_string("full_summary_")
    summary = generate_prefixed_string("summary_")
    return {
        "id": recipe_id,
        "name": name,
        "image": image,
        "full_summary": full_summary,
        "summary": summary,
    }


def generate_recommended_recipes(seedval):
    """
    Generates random recommended recipes.
    """
    seed(seedval)
    result = []
    for _ in range(0, randint(0, 10)):
        result.append(generate_recipe())
    return result


class DefaultRecommendedRecipesTest(unittest.TestCase):
    """
    The test case class to hold the actual test.
    """

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def setUp(self):
        """
        Sets up the test, including any needed input variables.
        """
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

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def runTest(self):
        """
        Runs the actual test.
        """
        app.init_app()

        for test in self.test_success_params:
            with patch(
                "app.routes.html.index.get_recommended_recipes_from_spoonacular"
            ) as get_recommended_recipes_from_spoonacular:
                # Mock out the values
                # index_get_current_user.return_value = None
                get_recommended_recipes_from_spoonacular.return_value = test[INPUT][
                    "recommended_recipes"
                ]

                # Render page
                page_content = ""
                with app.get_app().app_context():
                    page_content: str = index.index()

                # Validate page
                result = validate_page(test[INPUT]["recommended_recipes"], page_content)
                self.assertTrue(
                    result,
                    f"Assertion failed for input with seed {test[INPUT]['seedval']}",
                )


if __name__ == "__main__":
    unittest.main()
