# PieceMeal - Code Guides
This document describes methods for interfacing with the various parts of the PieceMeal application.

This is not a user guide; this is a developer guide. This means this document will not tell you how to navigate the PieceMeal website, but rather it is intended to be a guide for how to write code for PieceMeal.

## Table of Contents
- [PieceMeal - Code Guides](#piecemeal---code-guides)
  - [Table of Contents](#table-of-contents)
  - [Endpoints](#endpoints)
    - [User-Facing Endpoints](#user-facing-endpoints)
    - [API-Facing Endpoints](#api-facing-endpoints)
    - [Making Endpoints](#making-endpoints)
      - [Where to Place the Route](#where-to-place-the-route)
      - [Defining the Route File](#defining-the-route-file)
    - [Implementing Routes](#implementing-routes)
      - [Extracting Input Data](#extracting-input-data)
      - [Handling Database Calls](#handling-database-calls)
      - [Retrieving User Data](#retrieving-user-data)

## Endpoints
This guide describes what endpoints (i.e. routes) are, the kinds of endpoints PieceMeal has, and how to make an endpoint.

PieceMeal groups all of its endpoints into two primary categories: user-facing and API-facing.

### User-Facing Endpoints
User-facing endpoints (also called direct endpoints) are those which are designed to be used directly by the user. These kinds of endpoints are designed to be shown in the browser's address bar and always return HTML documents. Examples include the homepage (`/`), the account page (`/account`), and the login page (`/login`). User-facing endpoints should have simple naming schemes so they are easy to type and so they don't take up too much space in the address bar. Data which is not designed to be displayed should never be returned from these kinds of endpoints.

For a complete list of user-facing endpoints, as well as a bunch of other information on PieceMeal endpoints in general, see the documentation on [endpoints](endpoints.md).

### API-Facing Endpoints
API endpoints are those which are designed to process and return server data. These kinds of endpoints are designed to be called via code and typically always return JSON data (most API endpoints are RESTful). Examples include retrieving global recipe data (`/api/recipe-info/get`), updating user account info (`/api/account/update`), and sending friend requests (`/api/friends/send-request`). API endpoints should always begin with `/api` to designate them as such, and unless there is a specific implementation requirement, they should always be RESTful and only receive and return JSON data.

For a complete list of API-facing endpoints, as well as a bunch of other information on PieceMeal endpoints in general, see the documentation on [endpoints](endpoints.md).

### Making Endpoints
To make an endpoint in PieceMeal, there are a few guidelines that are good to follow to ensure maximum compatibility with the rest of the application.

Before making an endpoint, consider the following questions:
- What purpose does it achieve?
- Can it already be done with an existing endpoint?
- Does it require the server to perform?
- What kind of data will the server need from the client?
- What data will the server send back to the client once the request has been completed?

It's important to remember what an endpoint actually is: a way for the client to interface with the server. If the kind of data you need can already be obtained without having to go through the server to get it, then you probably don't need an endpoint for it.

Once you have definitive answers to all of these questions, then proceed to the next step.

#### Where to Place the Route
Before making the route, first decide if it is a direct (i.e. user-facing) route or an API route. All direct routes go in `/routes/direct`, and all API routes go in `/routes/api`. Once you've determined this, then determine which category the route belongs to. PieceMeal defines several categories for routes, such as ones related to user friends, account info, global recipe data, and more (the complete list can be found in the [endpoints documentation](endpoints.md)). If your route doesn't fit into any of these categories, then there are two ways to go about it: if it's an API route, you can place the route in the catch-all `misc.py` file, or for either direct or API routes, you can make a new category.

#### Defining the Route File
When designing a route file, here are the recommended steps to follow:

1. Write a module docstring. A docstring is a comment describing an element in a Python file, such as a function or a class. A module docstring is a docstring which is placed at the very top of the file and it describes what the file does as a whole. Docstrings should always be written in a triple-quoted string. As an example, here is the docstring for `/routes/api/account_info.py`:

```python
"""
This file contains endpoints related to user account information.
"""
```

2. Place all of your imports at the top of the module. Unless you need to import something in a very specific location, all imports should go at the top of the file, with Python library imports coming first (e.g. `os`, `json`, `base64`, etc.), 3rd-party library imports below that (e.g. Flask, PyCryptodome, Flask Login, etc.), and PieceMeal-related imports coming last. If you're ever not sure where an import should go, try running PyLint on your file. PyLint will let you know if your imports are in the wrong order or not placed correctly in the file. If you do need to place an import somewhere other than the top of the file however, make sure you disable the PyLint error and write a comment describing why you disabled it. For example, database tables have to be imported in very specific locations in `/database/database.py`, so here's an excerpt on how one of those are written:

```python
# pylint: disable=import-outside-toplevel
# This must be imported in this function because of
# the reliance on the instance of the Database class.
from .models import User
```

Notice how the first comment is a PyLint directive. It tells PyLint to ignore the problem for this import (but not for any other import in the file). Also notice how there is a comment directly below the PyLint directive explaining why the warning was disabled, and below this is the code which the directive is targeting.

3. Define a blueprint. A blueprint is a Flask-related object which is responsible for storing all of the information related to all of the routes which will be defined in your file. By using a blueprint to declare routes instead of the actual Flask application object, it means we can declare routes in files other than the main `app.py` file. When defining a blueprint, you must specify a unique identifier for the blueprint and you must tell the blueprint where the `static` and `templates` folders are. The blueprint ID should be unique across all blueprints, and a good naming scheme to use is `bp_<route_kind>_<route_category>`, where `<route_kind>` is the kind of routes your file contains (i.e. direct or API), and `<route_category>` is the category for the routes in your file (the category is usually also the name of the file). Here is the blueprint definition inside the `/routes/api/account_info.py` file:

```python
blueprint = Blueprint(
    "bp_api_account",
    __name__,
    template_folder=util.get_templates_folder(),
    static_folder=util.get_static_folder(),
)
```

Note the naming scheme for `bp_api_account`: this file defines API routes related to account information, which is clearly indicated in this file's blueprint ID. Also note the two functions `get_templates_folder()` and `get_static_folder()`. These two functions, which are defined in `/util.py`, are convenience functions for retrieving the location of the `templates` and `static` folders, respectively.

4. Define an initialization function. The `init()` function serves as a way to perform a one-time initialization for the whole file. Usually, this function is responsible for doing things like registering the blueprint with Flask and initializing the file's database object (if it has one). Here is the `init()` function for `/routes/api/account_info.py`:

```python
def init(app: Flask, database: Database):
    """
    Initializes this module.

    Args:
        app (Flask): The Flask application object.
        database (Database): The database object.
    """
    # pylint: disable=global-statement
    # We need to modify the global database object using this function
    global DATABASE

    DATABASE = database

    app.register_blueprint(blueprint)
```

This initialization function registers the file's blueprint by calling `app.register_blueprint()` and assigns the database object using `DATABASE = database`. Note the `blueprint` variable. This variable is the same one that was defined earlier in step 3.

Also, note the use of the PyLint disable directive. This is because `account_info.py` defines a global `DATABASE` variable which is used throughout the file to access the PieceMeal database, and it has to be initialized in this function. PyLint doesn't like it when you try to modify global variables, so we have to disable the warning here because we have to modify the global variable in this funciton.

5. Define your routes. Each route is defined using a single function with a `route()` decorator. This function should also have a docstring which describes its purpose, and since the function is a route, the docstring should describe the route itself and how it works. If you need a single endpoint to accept more than one request type (e.g. if you want to accept both `GET` and `POST` requests), define a new function for each request type. Here is an example which declares two routes, `/api/example/a` and `/api/example/b`, and route `b` accepts both `GET` and `POST` requests (function bodies have been ommitted):

```python
@blueprint.route("/api/example/a")
def route_a():
    """
    Performs action A and sends a confirmation back to the client.
    """

@blueprint.route("/api/example/b", methods=["GET"])
def route_b_get():
    """
    Performs action B for a GET request and sends a confirmation back to the client.
    """

@blueprint.route("/api/example/b", methods=["POST"])
def route_b_post():
    """
    Performs action B for a POST request.
    """
```

There are a couple of things to note here. First, notice that each route decorator (`@blueprint.route()`) is defined using the `blueprint` variable. This is the same variable defined in step 3.

For route A, since it only accepts `GET` requests, it doesn't need to define its accepted methods like in the route decorator for route B. Also notice how the same route `/api/example/b` is used for both `GET` and `POST` requests for route B, even though they're defined on separate functions.

6. Initialize your route. All route files must be initialized at some point, and depending on the kind of route file you're defining, this is done in one of two possible locations. For direct route files, they must be initialized in `/routes/direct/direct_routes.py`, and for API route files, they must be initialized in `/routes/api/api_routes.py`. These two files are called from the main `app.py` file to initialize all of the routes. To initialize your own route file, all you need to do is add a new line to the `init()` function inside of whichever `XXX_routes.py` file you're in which initializes your file. For example, if you have an API route file called `example.py` whose initialization function requires the Flask application instance and the PieceMeal database instance, inside of the `init()` function in `api_routes.py`, you would write:

```python
example.init(app, database)
```

Also note at the top of the file, you would need to import your route file. For example, in the `api_routes.py` file, you could add your import to the list that's already there, such as the following:

```python
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
    example,
)
```

### Implementing Routes
When implementing routes, there are some style guides to consider to ensure that all routes in PieceMeal are uniform.

For direct routes, the style guide is a bit more lax; the only real requirement for a direct route is that it returns HTML data (usually using `render_template()`).

For API routes, data should only ever be represented using JSON (unless you have a specific requirement that doesn't make this method feasible). This includes both data that is sent from the client to the server and data that is sent from the server to the client. There are also additional requirements for data sent from the server to the client. The server is expected to send a JSON object containing, at minimum, a `success` value which is a boolean representing the success of the request made to the server. If `success` is false, the server is also expected to send two additional values: `error_code`, which is an integer describing the kind of error that occurred, and `error_message`, which is a string describing the error that occurred.

To make this process easier, a couple of functions have been defined in `/routes/routing_util.py`.

`success_response()` will return a JSON object ready to be sent from the server to the client containing the necessary `success` value, as well as any other values you give it. For example, if you want to send two values `id` and `name`, those being integer and string values, respectively, all you would need to do inside your route function is write the following (assuming the ID and name values are stored in `some_id` and `some_name` variables):

```python
return success_response({"id": some_id, "name": some_name})
```

`error_response()` will return a JSON object ready to be sent from the server to the client containing the neccessary `success` value, as well as the `error_code`, and `error_message` values that you give it. For example, if you want to send the error code `5` and the error message `Failed to perform action`, in your route function you could write the following:

```python
return error_response(5, "Failed to perform action")
```

#### Extracting Input Data
For most API routes, you'll usually want to be able to send data from the client to the server. The way that this data is extracted depends on how the data was sent.

If you're sending JSON data, this is usually sent in the request body. To extract this data, you can use the function `get_json_data()` in `/routes/routing_util.py`. This function will raise an `InvalidEndpointArgsException` if the data is not present or is malformed, so make sure you handle the exception so it doesn't interfere with the route.

A common pattern for extracting JSON data consists of the following:

```python
try:
    data = get_json_data(request)
except InvalidEndpointArgsException:
    return error_response(1, "Invalid endpoint arguments")
```

This code snippet extracts the request JSON data and stores it in a `data` variable, and if there was an error extracting the data, it returns an error response value for the route.

The `request` variable being passed into `get_json_data()` is provided by Flask, which can be imported by writing `from flask import request`.

#### Handling Database Calls
When interfacing with the database, it's important to make sure you consider all possible actions that could occur during the call. This includes properly handling whatever data the database gives you and properly handling any exceptions that may be raised during the call.

A common pattern when interfacing with the database consists of the following:

```python
try:
    recipe = DATABASE.get_recipe_info(recipe_id)
except NoRecipeException:
    return error_response(1, "No recipe exists with the provided ID")
except DatabaseException:
    return error_response(0, "Database error")
```

This example assumes that a database instance has been defined using the global `DATABASE` variable and that a `recipe_id` local variable has been defined.

Note how multiple exceptions are caught. The `get_recipe_info` function has the possibility of raising multiple kinds of errors, so it's important to make sure that you handle all of them.

Also note the order in which the exceptions are handled. **This is important**: all exceptions raised by database calls are subclasses of the `DatabaseException` class. This means that technically for a call like the one above, you don't need to handle `NoRecipeException` explicitly because it would be covered under the handle for `DatabaseException`, however you may want to handle the errors separately because you may want to return more nuanced error information. If you want to handle the errors separately, you need to make sure you place the handler for `DatabaseException` **last**. If it is placed first, then all database errors will go to it rather than the more specific ones. As a general rule for exception handling, it's good practice to handle the more specific ones first and the more general ones last.

#### Retrieving User Data
If you want to get the current user inside of a route function, `/routes/routing_util.py` provides a function to get it. Calling `get_current_user()` will return the user object for the currently logged in user, or it will raise a `NoCurrentUserException` if no user is logged in. A typical case for using this function is in database calls, such as in the following example:

```python
try:
    user = get_current_user()
    recipes = DATABASE.get_recipes(user.id)
except NoCurrentUserException:
    return error_response(1, "Not logged in")
except DatabaseException:
    return error_response(0, "Database error")
```

Notice that we need to handle the case where the user is not logged in (`NoCurrentUserException`) and the case for when there is an error retrieving the user's recipes (`DatabaseException`). Also note that `NoCurrentUserException` is not a subclass of `DatabaseException`, so it must be handled separately.