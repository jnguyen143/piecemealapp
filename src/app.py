import flask
import dotenv
import os
from flask_login.utils import login_required
from database import database

dotenv.load_dotenv(dotenv.find_dotenv())

app = flask.Flask(__name__, template_folder=os.path.abspath("../templates"))
app.secret_key = os.getenv("FLASK_SECRET_KEY")
database.init(app)


@app.route("/login")
def login():
    return flask.render_template("login.html")


@app.route("/")
@login_required
def index():
    return flask.render_template("index.html")


@app.route("/signup")
def signup():
    return flask.render_template("signup.html")


@app.teardown_appcontext
def shutdown_session(exception=None):
    database.finalize()


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host=os.getenv("IP", "0.0.0.0"), port=os.getenv("PORT", 8080))
