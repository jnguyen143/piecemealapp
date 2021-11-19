"""
This file is responsible for collecting all of the
API routes into one file so the application need only
call init() from this module.
"""

from flask import Flask
from ...database.database2 import Database
from . import (
    global_recipes,
    global_ingredients,
    user_recipes,
    user_ingredients,
    friends,
    user_intolerances,
    users,
    account_info,
    misc,
)


def init(app: Flask, database: Database):
    """
    Initializes all API route modules.
    """
    global_recipes.init(app, database)
    global_ingredients.init(app, database)
    user_recipes.init(app, database)
    user_ingredients.init(app, database)
    friends.init(app, database)
    user_intolerances.init(app, database)
    users.init(app, database)
    account_info.init(app, database)
    misc.init(app, database)
