# pylint: disable=(E0401)
import unittest
from get_recommended_user_recipes import GetRecommendedUserRecipesTestCase
from get_recommended_user_ingredients import GetRecommendedUserIngredientsTestCase

# pylint: disable=(W0105)
# disabled error for string
# comment below
# being declared as useless
"""
Runs all mocked tests sequentially.

You must run this file from this directory.
The tests rely on relative paths to resolve some imports.
"""
# pylint: disable=(E0401)
# fixing invalid import error


# pylint: disable=(C0116)
# disabled except error
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
