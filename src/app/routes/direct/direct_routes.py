"""
This file is responsible for collecting all of the
direct routes into one file so the application need only
call init() from this module.
"""

from flask import Flask
from ...database.database2 import Database
from . import account, login, signup, index, profile


def init(app: Flask, database: Database):
    """
    Initializes all direct route modules.
    """
    account.init(app, database)
    login.init(app, database)
    signup.init(app, database)
    index.init(app, database)
    profile.init(app, database)
