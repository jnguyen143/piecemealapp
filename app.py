import flask
import dotenv
import os
from flask_login.utils import login_required
from flask_sqlalchemy import SQLAlchemy

dotenv.load_dotenv(dotenv.find_dotenv())

app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASEURL"] = os.getenv("DATABASE_URL")
app.config["SQULALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("LOGIN_KEY")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_ID = os.getenv("CLIENT_ID")
GOOGLE_SECRET = os.getenv("CLIENT_SECRET")
GOOGLE_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Gets rid of a warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
