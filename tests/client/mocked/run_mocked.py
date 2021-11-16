"""
Runs all mocked tests sequentially.

You must run this file from this directory. The tests rely on relative paths to resolve some imports.
"""

import unittest
from default_recommended_recipes import DefaultRecommendedRecipesTest
from recommended_ingredients import DefaultRecommendedIngredientsTest


def suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            DefaultRecommendedRecipesTest(),
            DefaultRecommendedIngredientsTest(),
        ]
    )
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
