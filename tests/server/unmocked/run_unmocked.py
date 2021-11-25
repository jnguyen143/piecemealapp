"""
Runs all unmocked tests sequentially.

You must run this file from this directory.
The tests rely on relative paths to resolve some imports.
"""
# pylint: disable=(E0401)
# fixing invalid import error

import unittest
from get_recommended_user_recipes import GetRecommendedUserRecipesTestCase
from get_recommended_user_ingredients import GetRecommendedUserIngredientsTestCase

# pylint: disable=(C0116)
def suite():
    # pylint: disable=(W0621)
    # disabled redefine error
    # as it does not affect code
    suite = unittest.TestSuite()
    suite.addTests(
        [GetRecommendedUserRecipesTestCase(), GetRecommendedUserIngredientsTestCase()]
    )
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
