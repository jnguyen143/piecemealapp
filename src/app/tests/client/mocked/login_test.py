"""
This file tests the correctness of default login page.
"""

import unittest
from unittest.mock import patch
from .... import app
from ....routes.html import login


class DefaultLoginTest(unittest.TestCase):
    """
    The test case class for the login test.
    """

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def setUp(self):
        """
        Sets up the test.
        No setup needs to be performed for this client test.
        """

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def runTest(self):
        """
        Runs the test.
        """
        app.init_app()

        with patch("app.routes.html.login.get_login_auth_status") as auth_status:
            auth_status.return_value = 0

            # Render page
            page_content = ""
            with app.get_app().app_context():
                page_content: str = login.login()

            self.assertTrue(page_content.find("Failed to log in") == -1)
            self.assertFalse(
                page_content.find("Log in through your google account") == -1
            )


if __name__ == "__main__":
    unittest.main()
