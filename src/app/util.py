"""
Utility functions for the entire application.
"""
import pathlib


def get_or_raise(dictionary: dict, key: str, error):
    """
    Attempts to return the value from the dictionary with the specified key.
    If the dictionary does not have the value, the specified error function
    will be used to generate and raise an error.
    """

    try:
        return dictionary[key]
    except KeyError as err:
        raise error from err


def get_or_default(dictionary: dict, key: str, default_value):
    """
    Attempts to return the value from the dictionary with the specified key.
    If the dictionary does not have the value, the specified default value will be used instead.
    """

    try:
        return dictionary[key]
    except KeyError:
        return default_value


def get_or_default_func(dictionary: dict, key: str, default_value_func):
    """
    Attempts to return the value from the dictionary with the specified key.
    If the dictionary does not have the value, the specified default value function
    will be executed and used instead.
    """

    try:
        return dictionary[key]
    except KeyError:
        return default_value_func()


def dict_list_contains(lst: list[dict], key: str, value) -> bool:
    """
    Returns true if any of the dictionaries in the provided list contains
    a key-value pair which matches the provided pair.
    """
    for dct in lst:
        if key in dct and dct[key] == value:
            return True
    return False


def get_application_root_dir() -> str:
    """
    Returns the absolute path to the application root directory.

    Returns:
        The absolute path to the application root directory.
    """
    # The relative path of this file is /src/app/util.py,
    # so file->parent->parent = '/app' (root directory)
    return pathlib.Path(__file__).parent.parent.resolve()


def get_templates_folder() -> str:
    """
    Returns the absolute path to the "templates" directory.

    Returns:
        The absolute path of the "templates" directory as a string.
    """
    # The relative path of this file is /src/app/util.py,
    # so file->parent->parent = '/' (root directory)
    return pathlib.Path(__file__).parent.parent.parent.joinpath("templates").resolve()


def get_static_folder() -> str:
    """
    Returns the absolute path to the "static" directory.

    Returns:
        The absolute path of the "static" directory as a string.
    """
    # The relative path of this file is /src/app/util.py,
    # so file->parent->parent = '/' (root directory)
    return pathlib.Path(__file__).parent.parent.parent.joinpath("static").resolve()
