"""
Runs all unmocked tests sequentially.

You must run this file from this directory.
The tests rely on relative paths to resolve some imports.
"""

import sys
import unittest
from .get_recommended_user_recipes import GetRecommendedUserRecipesTestCase
from .get_recommended_user_ingredients import GetRecommendedUserIngredientsTestCase


def suite():
    """
    Returns the test suite containing all unmocked server tests.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        [GetRecommendedUserRecipesTestCase(), GetRecommendedUserIngredientsTestCase()]
    )
    return test_suite


def run():
    """
    Runs all unmocked server tests.
    """
    result = unittest.TextTestRunner().run(suite()).wasSuccessful()
    if not result:
        sys.exit(1)
