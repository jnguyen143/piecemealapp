"""
Runs all mocked tests sequentially.

You must run this file from this directory. The tests rely on relative paths to resolve some imports.
"""

import unittest
from get_recommended_user_recipes import GetRecommendedUserRecipesTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            GetRecommendedUserRecipesTestCase(),
        ]
    )
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
