"""
Runs all mocked tests sequentially.

You must run this file from this directory.
The tests rely on relative paths to resolve some imports.
"""
import sys
import unittest
from .default_recommended_recipes import DefaultRecommendedRecipesTest
from .login_test import DefaultLoginTest


def suite():
    """
    Executes all of the mocked client tests together as a test suite.
    """
    test_suite = unittest.TestSuite()
    test_suite.addTests([DefaultRecommendedRecipesTest(), DefaultLoginTest()])
    return test_suite


def run():
    """
    Executes all mocked client tests.
    """
    result = unittest.TextTestRunner().run(suite()).wasSuccessful()
    if not result:
        sys.exit(1)
