import flask
import dotenv
import os
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy

dotenv.load_dotenv(dotenv.find_dotenv())

app = flask.Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql" + os.getenv("DATABASE_URL")[8:]

# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


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
    db.session.close()


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host=os.getenv("IP", "0.0.0.0"), port=os.getenv("PORT", 8080))
