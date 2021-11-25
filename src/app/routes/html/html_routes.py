"""
This file is responsible for collecting all of the
HTML routes into one file so the application need only
call init() from this module.
"""

from flask import Flask
from ...database.database import Database
from . import account, login, signup, index, profile, users, error


def init(app: Flask, database: Database):
    """
    Initializes all HTML route modules.
    """
    account.init(app, database)
    login.init(app, database)
    signup.init(app, database)
    index.init(app, database)
    profile.init(app, database)
    users.init(app, database)
    error.init(app)
