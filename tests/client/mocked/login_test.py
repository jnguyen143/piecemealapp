"""
This file tests the correctness of default login page.
"""

import unittest
from unittest.mock import patch
import sys
import pathlib
from ....src.app import app
from ....src.app.routes.html import login


def init_app_module_dir():
    """
    Adds the directory containing `app.py` to the system path.
    This lets you import the app module.
    """
    path = str(
        pathlib.Path(__file__).parent.parent.parent.parent.joinpath("src").resolve()
    )
    sys.path.append(path)


class DefaultLoginTest(unittest.TestCase):
    """
    The test case class for the login test.
    """

    def setUp(self):
        """
        Sets up the test.
        No setup needs to be performed for this client test.
        """
        pass

    def runTest(self):
        """
        Runs the test.
        """
        # init_app_module_dir()
        # If the below comment is not present, pylance will generate an import warning. We know the import is valid because the above function call injects the required module directory.
        # pylint: disable=import-error
        # This import is valid
        # import app  # pylint: disable=import-outside-toplevel

        app.init_app()

        # Like the app module above, this must be imported
        # from routes import login  # pylint: disable=import-outside-toplevel

        with patch("routes.login.get_login_auth_status") as auth_status:
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
