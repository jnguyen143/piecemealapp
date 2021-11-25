"""
==================== COMMON API DEFINITIONS ====================
This file defines common types and functions used across all or multiple API files.
"""
import requests


class UndefinedApiKeyException(Exception):
    """
    Raised when an API call is made but the required key to make the call has not been defined.
    This is usually due to the api key environment variable not being defined correctly.
    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message


class RequestException(Exception):
    """
    Raised when an API call cannot be made due to an error during the actual request.
    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message


class MalformedResponseException(Exception):
    """
    Raised when an API call is made but the response is invalid or contains malformed data.
    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message


def api_get_json(url: str, headers: dict = None, params: dict = None) -> dict:
    """
    Makes a GET request to the specified endpoint and returns the response as JSON data.

    Args:
        url (str): The destination URL used to retrieve the data.
        headers (dict): The headers to use in the request. This argument is optional.
        params (dict): The parameters to use in the request. This argument is optional.

    Returns:
        A JSON object representing the response data.

    Raises:
        RequestException: If the request was unable to be completed.
        MalformedResponseException: If the response did not return a valid status
            code or produced invalid JSON data.
    """

    response = None
    try:
        response = requests.get(url, headers=headers, params=params)
    except Exception as e:
        raise RequestException(f"Failed to make GET request: {str(e)}") from e

    if not response.ok:
        raise MalformedResponseException(
            f"Invalid response (received {response.status_code})"
        )

    try:
        result = response.json()
        return result
    except Exception as e:
        raise MalformedResponseException(f"Malformed JSON; details: {str(e)}") from e
