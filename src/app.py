import flask
import dotenv
import os
from database import database
import routes.util

app = None


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

    # Load the environment file
    env_path = dotenv.find_dotenv()
    if env_path == "":
        raise Exception("Failed to load environment file")
    dotenv.load_dotenv(env_path)

    # Create the application
    app = flask.Flask(__name__, static_folder=routes.util.get_static_folder())
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    db = None

    # Initialize the database
    try:
        db = database.Database(app)
    except database.DatabaseException as e:
        raise Exception(f"Failed to initialize database ({str(e)})")

    # Register the blueprints
    from routes import index, login, signup, userdata

    userdata.set_db_obj(db)

    app.register_blueprint(index.get_blueprint())
    app.register_blueprint(login.get_blueprint())
    app.register_blueprint(signup.get_blueprint())
    app.register_blueprint(userdata.get_blueprint())


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

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        database.finalize()

    start_app()
