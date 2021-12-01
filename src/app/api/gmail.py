"""
This file contains the GMAIL API authorization and automated email processing for
the Service Account
"""
from __future__ import print_function
from os import getenv
from email.mime.text import MIMEText
from googleapiclient.discovery import build
import pybase64
from google.oauth2 import service_account

# Email sending confirmation email
EMAIL_FROM = getenv("ADMIN_EMAIL")


def send_confirmation_email(new_user_email):
    """

    Initiates the issuance of account creation confirmation email

    Args:
        New user email address provided during signup process

    """

    # Email from user must be retrieved and stored in EMAIL_TO
    email_to = new_user_email
    email_subject = "Welcome to pieceMeal!"

    with open("confirmation.txt", "r", encoding="utf-8") as file:
        message = file.read()

    email_content = message

    # Login into service
    service = service_account_login()

    # Call the Gmail API
    message = create_registration_confirm_message(
        EMAIL_FROM, email_to, email_subject, email_content
    )

    send_message(service, "me", message)


class ServiceKeyException(Exception):
    """
    Raised when the json file containing the service account's secret key is not found
    """

    def __init__(self, message=""):
        super().__init__()
        self.message = message


def service_account_login():
    """
    Requests credential authorization on behalf of service acount admin user

    Args:
        Indirect calling of service-key.json

    Returns:
        Service built for specified authorized service account user - Admin
    """
    scopes = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://mail.google.com",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.settings.sharing",
        "https://www.googleapis.com/auth/gmail.settings.basic",
    ]

    try:
        service_account_file = "service-key.json"
    except ServiceKeyException:
        pass

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes
    )

    delegated_credentials = credentials.with_subject(EMAIL_FROM)

    service = build("gmail", "v1", credentials=delegated_credentials)

    return service


def create_registration_confirm_message(sender, new_user, subject, message_text):
    """
    Creates automated message for user signup confirmation

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message["to"] = new_user
    message["from"] = sender
    message["subject"] = subject
    message_string = bytes(str(message), "utf-8")
    # return {"raw": pybase64.urlsafe_b64encode(message.as_string())}
    return {"raw": pybase64.urlsafe_b64encode(message_string).decode("utf-8")}


def send_message(service, user_id, message):
    """
    Sends an email message

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message: Message to be sent.

    Returns:
      Sent Message.
    """

    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )

        print(f"Message Id: {message['id']}")

    # pylint: disable=broad-except
    # Gmail API could return any number of errors and we want to catch them all.
    except Exception as error:
        print(f"An error occurred: {error}")
