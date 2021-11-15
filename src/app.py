import flask
import dotenv
import os
from database import database
import routes.util as util


# Before anything else, make sure we have 3.9 or greater
import sys

MIN_PYTHON_VERSION = (3, 9)
if sys.version_info < MIN_PYTHON_VERSION:
    sys.exit(
        "Python %s.%s or greater is required to run this application.\n"
        % MIN_PYTHON_VERSION
    )

app = None
db: database.Database = None


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
        Exception: If there was a problem initializing the application or any of its related components.
    """
    global app
    global db

    # Load the environment file
    env_path = dotenv.find_dotenv()
    if env_path == "":
        raise Exception("Failed to load environment file")
    dotenv.load_dotenv(env_path)

    # Create the application
    app = flask.Flask(__name__, static_folder=util.get_static_folder())
    app.secret_key = os.getenv("FLASK_SECRET_KEY")

    # XXX: This is for debugging only!
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Initialize the database
    try:
        db = database.Database(app)
    except database.DatabaseException as e:
        raise Exception(f"Failed to initialize database ({str(e)})")

    # Register the blueprints
    import routes.index, routes.login, routes.signup, routes.profile, routes.search, routes.userdata, routes.account, routes.logout

    routes.userdata.init(db)
    routes.login.init(app, db)
    routes.account.init(db)

    app.register_blueprint(routes.index.get_blueprint())
    app.register_blueprint(routes.login.get_blueprint())
    app.register_blueprint(routes.signup.get_blueprint())
    app.register_blueprint(routes.userdata.get_blueprint())
    app.register_blueprint(routes.profile.get_blueprint())
    app.register_blueprint(routes.search.get_blueprint())
    app.register_blueprint(routes.account.get_blueprint())
    app.register_blueprint(routes.logout.get_blueprint())

    # Register the teardown context
    app.teardown_appcontext(shutdown_session)


def start_app():
    """
    Starts the application.

    `init_app()` must be called prior to calling this function.

    Raises:
        Exception: If the application was not initialized.
    """
    if app == None:
        raise Exception("Application not initialized")

    app.run(debug=True)


if __name__ == "__main__":
    init_app()
    start_app()
