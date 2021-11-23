"""
==================== ROUTING UTILITIES ====================
This file defines utility functions for routing files.
"""
import pathlib


def get_application_root_dir() -> str:
    """
    Returns the absolute path to the application root directory.

    Returns:
        The absolute path to the application root directory.
    """
    # The relative path of this file is /src/routes/util.py, so file->parent->parent->parent = '/' (root directory)
    return pathlib.Path(__file__).parent.parent.parent.resolve()


def get_templates_folder() -> str:
    """
    Returns the absolute path to the "templates" directory.

    Returns:
        The absolute path of the "templates" directory as a string.
    """
    # The relative path of this file is /src/routes/util.py, so file->parent->parent->parent = '/' (root directory)
    return pathlib.Path(__file__).parent.parent.parent.joinpath("templates").resolve()


def get_static_folder() -> str:
    """
    Returns the absolute path to the "static" directory.

    Returns:
        The absolute path of the "static" directory as a string.
    """
    # The relative path of this file is /src/routes/util.py, so file->parent->parent->parent = '/' (root directory)
    return pathlib.Path(__file__).parent.parent.parent.joinpath("static").resolve()
