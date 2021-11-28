"""
This file contains error-handling functions, such as ones that handle 404 or 500 errors.
"""
from flask import Flask, render_template
from werkzeug.utils import redirect


def init(app: Flask):
    """
    Initializes this module and registers its error handlers.
    """
    app.register_error_handler(404, error_not_found)
    app.register_error_handler(500, error_internal)
    app.register_error_handler(401, error_not_signed_in)


def error_not_found(_):
    """
    This error occurs when the user attempts to retrieve a resource that does not exist.
    """
    return (
        render_template(
            "error.html",
            header="Page Not Found",
            tagline="You can't order off-menu here.",
            message=["Sorry, that page doesn't exist."],
        ),
        404,
    )


def error_internal(_):
    """
    This error occurs when the server had a problem performing a task.
    """
    return (
        render_template(
            "error.html",
            header="Internal Server Error",
            tagline="We burnt your order, sorry about that.",
            message=[
                "Sorry, we can't complete your request right now.",
                "Please try again later!",
            ],
        ),
        500,
    )


def error_not_signed_in(_):
    """
    This error occurs when the user attempted to access a page
    for which they were not authorized to access.

    This is usually because they are not logged in.

    Triggering this error will redirect the user to the login page.
    """

    return redirect("/login")
