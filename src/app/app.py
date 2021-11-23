"""
Python app.py file containing the app initiation, calling of the database object,
and routes registration
"""
import os
import sys
import flask
import dotenv
from . import util
from .database import database
from .routes import routes

dotenv.load_dotenv(dotenv.find_dotenv())

# Before anything else, make sure we have python3.9 or greater
MIN_PYTHON_VERSION = (3, 9)
if sys.version_info < MIN_PYTHON_VERSION:
    sys.exit(
        f"Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}"
        + " or greater is required to run this application.\n"
    )

APP_OBJ = None
DATABASE: database.Database = None


def init_app():
    """
    Initializes the application.

    This function performs the following operations:
    - Finds and loads the environment file
    - Creates the application context
    - Initializes the database
    - Registers the application blueprints

    Raises:
        Exception: If there was a problem initializing the application or
        any of its related components.
    """
    # pylint: disable=global-statement
    global APP_OBJ
    global DATABASE

    # Load the environment file
    env_path = dotenv.find_dotenv()
    if env_path != "":
        dotenv.load_dotenv(env_path)

    # Create the application
    APP_OBJ = flask.Flask(__name__, static_folder=util.get_static_folder())
    APP_OBJ.secret_key = os.getenv("FLASK_SECRET_KEY")

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Initialize the database
    try:
        DATABASE = database.Database(APP_OBJ)
    except database.DatabaseException as exc:
        raise Exception("Failed to initialize database") from exc

    # Initialize the routes
    routes.init(APP_OBJ, DATABASE)


def get_app():
    """
    Returns the application object.
    """
    return APP_OBJ


def start_app():
    """
    Starts the application.

    `init_app()` must be called prior to calling this function.

    Raises:
        Exception: If the application was not initialized.
    """
    if APP_OBJ is None:
        raise Exception("Application not initialized")
    # Disabling because os.getenv is retrieving a port and not a string
    # pylint: disable=W1508
    # APP_OBJ.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
    APP_OBJ.run(debug=True)
