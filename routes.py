import flask
import json
import os
from flask_sqlalchemy import SQLAlchemy
import dotenv
import requests
import datetime
import oauthlib
import OpenSSL
from oauthlib.oauth2 import WebApplicationClient
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
    UserMixin,
)


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASEURL"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("LOGIN_KEY")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_ID = os.getenv("CLIENT_ID")
GOOGLE_SECRET = os.getenv("CLIENT_SECRET")
GOOGLE_URL = "https://accounts.google.com/.well-known/openid-configuration"

db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_name):
    return User.query.get(user_name)


client = WebApplicationClient(GOOGLE_ID)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    userID = db.Column(db.String(255))
    username = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)
    profile_pic = db.Column(db.String(100))


db.create_all()


def get_google_provider_cfg():
    return requests.get(GOOGLE_URL).json()


@app.route("/login")
def login():
    google_provider = get_google_provider_cfg()
    authorization_endpoint = google_provider["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=flask.request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return flask.redirect(request_uri)


@app.route("/login/callback")
def callback():
    code = flask.request.args.get("code")
    google_provider = get_google_provider_cfg()
    token_endpoint = google_provider["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=flask.request.url,
        redirect_url=flask.request.base_url,
        code=code,
    )

    token_response = requests.post(
        token_url, headers=headers, data=body, auth=(GOOGLE_ID, GOOGLE_SECRET)
    )
    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        user_id = userinfo_response.json()["sub"]
        user_email = userinfo_response.json()["email"]
        user_pfp = userinfo_response.json()["picture"]
        user_name = userinfo_response.json()["given_name"]

    user = User(
        userID=user_id, username=user_name, email=user_email, profile_pic=user_pfp
    )
    db.session.add(user)
    db.session.commit()

    login_user(user)
    return flask.redirect(flask.url_for("main"))


@app.route("/")
def main():
    if current_user.is_authenticated:
        return flask.render_template("index.html")
    return flask.render_template("login.html")


@app.route("/index")
def index():
    return flask.render_template("index.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
