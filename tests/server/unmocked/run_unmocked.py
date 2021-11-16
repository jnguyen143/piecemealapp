"""
Runs all unmocked tests sequentially.

You must run this file from this directory. The tests rely on relative paths to resolve some imports.
"""

import unittest
from get_recommended_user_recipes import GetRecommendedUserRecipesTestCase
from get_recommended_user_ingredients import GetRecommendedUserIngredientsTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [GetRecommendedUserRecipesTestCase(), GetRecommendedUserIngredientsTestCase()]
    )
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
