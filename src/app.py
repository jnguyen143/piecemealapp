"""
Python app.py file containing the app initiation, calling of the database object, 
and routes registration
"""
import os
import sys
import flask
import dotenv

# pylint: disable=import-error
# This import is valid
from database import database
import routes.util as util
import routes.index as index

dotenv.load_dotenv(dotenv.find_dotenv())

# Before anything else, make sure we have python3.9 or greater
MIN_PYTHON_VERSION = (3, 9)
if sys.version_info < MIN_PYTHON_VERSION:
    sys.exit(
        "Python %s.%s or greater is required to run this application.\n"
        % MIN_PYTHON_VERSION
    )

APP = None
db: database.Database = None

# pylint: disable=W0613
"""Function that shuts down database session"""


def shutdown_session(exception=None):
    db.finalize()


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
    # pylint: disable=W0603, C0103, W0601
    global app
    global db

    # Load the environment file
    env_path = dotenv.find_dotenv()
    if env_path != "":
        dotenv.load_dotenv(env_path)

    # Create the application
    app = flask.Flask(__name__, static_folder=util.get_static_folder())
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Initialize the database
    try:
        DB = database.Database(app)
    except database.DatabaseException as e:
        raise Exception(f"Failed to initialize database ({str(e)})")

    # pylint: disable=C0415
    # Register the blueprints
    import routes.login
    import routes.signup
    import routes.profile
    import routes.search
    import routes.userdata
    import routes.account
    import routes.logout

    routes.userdata.init(db)
    routes.login.init(app, db)
    routes.account.init(db)
    index.init(db)
    routes.profile.init(db)

    app.register_blueprint(index.get_blueprint())
    app.register_blueprint(routes.login.get_blueprint())
    app.register_blueprint(routes.signup.get_blueprint())
    app.register_blueprint(routes.userdata.get_blueprint())
    app.register_blueprint(routes.profile.get_blueprint())
    app.register_blueprint(routes.search.get_blueprint())
    app.register_blueprint(routes.account.get_blueprint())
    app.register_blueprint(routes.logout.get_blueprint())

    # Register the teardown context
    app.teardown_appcontext(shutdown_session)


# Function that returns index module
def get_index_module():
    return index


# Function that returns app object/variable
def get_app():
    return app


# Function that starts application and allows for it to run on specified port
def start_app():
    """
    Starts the application.

    `init_app()` must be called prior to calling this function.

    Raises:
        Exception: If the application was not initialized.
    """
    if app == None:
        raise Exception("Application not initialized")
    # Disabling because os.getenv is retrieving a port and not a string
    # pylint: disable=W1508
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))


if __name__ == "__main__":
    init_app()
    start_app()
