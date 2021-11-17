"""
This file tests the correctness of default login page.
"""

import unittest
from unittest.mock import patch


def init_app_module_dir():
    import sys
    import pathlib

    path = str(
        pathlib.Path(__file__).parent.parent.parent.parent.joinpath("src").resolve()
    )
    sys.path.append(path)


class DefaultLoginTest(unittest.TestCase):
    def setUp(self):
        pass

    def runTest(self):
        init_app_module_dir()
        # If the below comment is not present, pylance will generate an import warning. We know the import is valid because the above function call injects the required module directory.
        # pylint: disable=import-error
        # This import is valid
        import app  # pyright: reportMissingImports=false

        app.init_app()

        from routes import login

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
