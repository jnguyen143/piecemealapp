import os


def get_public_key():
    return os.getenv("APP_PUBLIC_KEY")


def get_private_key():
    return os.getenv("APP_PRIVATE_KEY")
