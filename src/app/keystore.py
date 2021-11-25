"""
Defines functions relating to server API keys.
"""

import os


def get_public_key():
    """
    Returns the server's public key.
    """
    return os.getenv("APP_PUBLIC_KEY")


def get_private_key():
    """
    Returns the server's private key.
    """
    return os.getenv("APP_PRIVATE_KEY")
