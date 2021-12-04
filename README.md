# App URL
https://www.piecemealapp2.com/

Alternative URL: https://piecemealapp2.herokuapp.com/
# Overview
This documentation describes the functionality of the pieceMeal app as well as the technical specifications required to run the app.
## Description
The app is a food-based service that takes in a user's input based on desired ingredients and returns a series of recipes that feature the ingredients requested. The app would tailor to user experience and have the recipes and ingredients saved to a user profile that the user can preview at any time. The search function of the app can have various filters applied to the results such as cuisine, allergies, and intolerances. The app supports two methods of accounts: a manual version within the app where a simple username and password is created, and a Google-based one which supports connecting an existing Google account and creates a profile based on the information existing from the account.

# APIs
The following APIs were utilized in the creation of the pieceMeal app:
* Spoonacular: the main API utilized for pieceMeal, this app provides for numerous functions such as retrieving recipes and filtering them based off certain parameters for the user.
* Google Oauth2: The main provider of authentication, this API utilizes OpenID functionality to connect a Google account to the app and pull information that can be used to create an app profile for it.
* Google Gmail: This API controls automated emailing to all the accounts as a way of notifying users when they join Spponacular
## Note
The credentials for the Google and Spoonacular API must be stored in a .env file, which cannot be pushed to Github by creating a .gitignore file and adding ".env" to it for privacy reasons.

## Requirements
The following packages are required to run the app, all of which are provided in the requirements.txt file:
* Flask: the main framework for the app that provides for many of the functions within the app
* Flask-Login: provides authentication on the flask server with various functions
* Flask_SQLAlchemy: provides the main framework for setting up the database for storing user information
* Python-dotenv: provides function for retrieving data from .env file (currently hidden)
* Requests: utilized for formatting data pulled from user
* requests_oauthlib: connects the Google API functions to Flask in a more comprehensive form
* pyOpenSSL: enables secure connection with https (required for bypassing warning)
* Google APIs: Various Google API packages that enable the Gmail service to work

## Installation
Run the command `pip3 install -r requirements.txt.` to install the dependencies required for running the app.

The app utilizes 2048-bit RSA encryption to provide in-house authentication between the client and the server through the usage of two keys generated from two separate files, public_key.pem and private_key pem. To generate these files run the following commands in a Python terminal:
```from Crypto.PublicKey import RSA
keypair = RSA.generate(2048)
with open("private_key.pem", "wb") as f:
    f.write(keypair.exportKey())
with open("public_key.pem", "wb") as f:
    f.write(keypair.publickey().exportKey()) 