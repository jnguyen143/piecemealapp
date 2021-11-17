"""
Runs all mocked tests sequentially.

You must run this file from this directory.
The tests rely on relative paths to resolve some imports.
"""
# pylint: disable=(E0401)
import unittest
from default_recommended_recipes import DefaultRecommendedRecipesTest
from get_similar_recipes import GetSimilarRecipesTest
from login_test import DefaultLoginTest

# pylint: disable=(C0116)
def suite():
    # pylint: disable=(W0621)
    # disabled redefine error
    # as it does not affect code
    suite = unittest.TestSuite()
    suite.addTests(
        [
            DefaultRecommendedRecipesTest(),
            DefaultLoginTest()
            # GetSimilarRecipesTest()
        ]
    )
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
