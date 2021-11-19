"""
This file is responsible for collecting all of the
routes into one file so the application need only
call init() from this module.
"""
from flask import Flask
from ..database.database2 import Database
from .api import api_routes
from .direct import direct_routes


def init(app: Flask, database: Database):
    """
    Initializes all route modules.
    """
    api_routes.init(app, database)
    direct_routes.init(app, database)
