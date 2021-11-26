# PieceMeal Endpoints
This file details the list of available endpoints for PieceMeal, including user-facing endpoints and server-oriented API endpoints.

## Table of Contents
- [PieceMeal Endpoints](#piecemeal-endpoints)
  - [Table of Contents](#table-of-contents)
  - [HTML Endpoints](#html-endpoints)
    - [Homepage](#homepage)
    - [Login](#login)
    - [Signup](#signup)
    - [Account Info](#account-info)
  - [API Endpoint Objects](#api-endpoint-objects)
    - [Recipe](#recipe)
    - [Ingredient](#ingredient)
    - [User](#user)
    - [Intolerance](#intolerance)
  - [API Endpoints](#api-endpoints)
    - [Global Recipe Info](#global-recipe-info)
      - [Get Recipe Info](#get-recipe-info)
      - [Search for Recipes](#search-for-recipes)
      - [Get Similar Recipes](#get-similar-recipes)
      - [Get Random Recipes](#get-random-recipes)
    - [Global Ingredient Info](#global-ingredient-info)
      - [Get Ingredient Info](#get-ingredient-info)
      - [Search for Ingredients](#search-for-ingredients)
    - [User-Saved Recipes](#user-saved-recipes)
      - [Get User Recipes](#get-user-recipes)
      - [Add User Recipe](#add-user-recipe)
      - [Delete User Recipe](#delete-user-recipe)
      - [Get Top User Recipes](#get-top-user-recipes)
      - [Get Top Friend Recipes](#get-top-friend-recipes)
      - [Get Recommended Recipes](#get-recommended-recipes)
    - [User-Saved Ingredients](#user-saved-ingredients)
      - [Get User Ingredients](#get-user-ingredients)
      - [Add User Ingredient](#add-user-ingredient)
      - [Delete User Ingredient](#delete-user-ingredient)
      - [Get Top User Ingredients](#get-top-user-ingredients)
      - [Get Top Friend Ingredients](#get-top-friend-ingredients)
    - [Friends](#friends)
      - [Get Friends](#get-friends)
      - [Send a Friend Request](#send-a-friend-request)
      - [Handle a Friend Request](#handle-a-friend-request)
      - [Get Sent Requests](#get-sent-requests)
      - [Get Received Requests](#get-received-requests)
    - [User Intolerances](#user-intolerances)
      - [Get User Intolerances](#get-user-intolerances)
      - [Add User Intolerance](#add-user-intolerance)
      - [Delete User Intolerance](#delete-user-intolerance)
    - [Users](#users)
      - [Search for Users](#search-for-users)
      - [Get a User](#get-a-user)
    - [Account Info](#account-info-1)
      - [Update Account Info](#update-account-info)
      - [Update Password](#update-password)
      - [Delete Account](#delete-account)
    - [Miscellaneous](#miscellaneous)
      - [Get Server Public Key](#get-server-public-key)
      - [Initiate Login Flow](#initiate-login-flow)
      - [Initiate Signup Flow](#initiate-signup-flow)

## HTML Endpoints
HTML endpoints are routes designed to be visited directly by the user.
These kinds of routes return raw HTML data to be rendered by the user's browser.

### Homepage
`/` - Returns the index page. The content of the index page will be different depending if the user is signed in.

### Login
`/login` - Returns the login page.

### Signup
`/signup` - Returns the signup page.

### Account Info
`/account` - Returns the account page.

## API Endpoint Objects
This section describes the layout for the possible JSON objects that may be returned from some of the API calls.

### Recipe
A recipe object contains information describing a recipe.

Attributes
- `id (int)`: The ID of the recipe.
- `name (str)`: The name of the recipe.
- `image (str)`: The URL for an image of the recipe.
- `summary (str)`: The (brief) summary for the recipe. This field may be an empty string.
- `full_summary (str)`: The full summary for the recipe. This field may be an empty string.

### Ingredient
An ingredient object contains information describing an ingredient.

Attributes
- `id (int)`: The ID of the ingredient.
- `name (str)`: The name of the ingredient.
- `image (str)`: The URL for an image of the ingredient.

### User
A user object contains information describing a user.

User objects contain minimal information about users; they do not contain sensitive fields such as emails or authentication methods.

Attributes
- `id (str)`: The ID of the user.
- `username (str)`: The username of the user.
- `given_name (str)`: The user's given name. This value is only present if the user allows their name to be shared publicly.
- `family_name (str)`: The user's family name. This value is only present if the user allows their name to be shared publicly.
- `profile_image (str)`: The URL for the user's profile image.
- `profile_visibility (int)`: The user's profile visibility.
- `creation_date (str)`: The user's account creation date as a string with the format `DD MM, YYYY`, where `MM` is the month spelled out completely. This value is only present if the user allows their account creation date to be shared publicly.

### Intolerance
An intolerance object contains information describing a food intolerance.

Attributes
- `id (int)`: The ID of the intolerance.
- `name (str)`: The name of the intolerance.

## API Endpoints
API endpoints are routes designed to be called programmatically. They are not intended to be visited directly by the user.
All API endpoints, unless otherwise indicated, are REST-compliant.

As a general rule, if any of the API endpoints fail to complete the request, they will return a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed. For failed requests, this value will always be false.
- `error_code (int)`: The integer error code detailing what kind of error occurred. The possible values for this field are specific to the request being made.
- `error_message (str)`: The message describing what kind of error occurred.

### Global Recipe Info
#### Get Recipe Info
`GET /api/recipe-info/get` - Returns a JSON object containing the recipe information for the recipe with the specified ID.

Args
- `id (int)`: The ID of the target recipe.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `recipe`: A [`Recipe`](#recipe) object.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.
- 2 - No recipe exists with the provided ID.

#### Search for Recipes
`GET /api/recipe-info/search` - Returns a list of recipes which match the specified search query.

Args
- `query (str)`: The search query to use.
- `intolerances (list[str])`: The list of intolerances to use as a filter. This argument is optional.
- `cuisines (list[str])`: The list of cuisines to use as a filter. This argument is optional.
- `diets (list[str])`: The list of diets to use as a filter. This argument is optional.
- `ingredients (list[int])`: The list of [`Ingredient`](#ingredient) IDs to use as a filter. This argument is optional.
- `max_prep_time (int)`: The maximum prep time for the recipes (in minutes). This argument is optional.
- `sort_by (str)`: The criteria to use to sort the results. This argument is optional.
- `offset (int)`: The offset into the results to start at. This argument is optional and by default is 0.
- `limit (int)`: The maximum number of results to return. This argument is optional and by default is 10.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `recipes`: A list of [`Recipe`](#recipe) objects.
- `total_results`: An integer describing the maximum number of available results.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.

#### Get Similar Recipes
`GET /api/recipe-info/get-similar` - Returns a list of recipes which are similar to the specified recipe.

Args
- `id (int)`: The recipe ID to use as a reference for the recipes to retrieve.
- `limit (int)`: The maximum number of results to return. This argument is optional and by default is 10.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `recipes`: A list of [`Recipe`](#recipe) objects.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.
- 2 - The specified recipe does not exist.

#### Get Random Recipes
`GET /api/recipe-info/get-random` - Returns a random list of recipes.

Args
- `source (str)`: Where to get the recipes. This value is optional (by default it is `cache`) and must be one of the following:
  - `cache`: Only look up recipes stored in PieceMeal's own database.
  - `external`: Only look up recipes from external sources (i.e. Spoonacular). These results will then be cached.
  - `mixed`: Return a mixture (approximately half and half) of cached and external recipes. Any external recipes will be cached once they have been retrieved.
- `limit (int)`: The maximum number of results to return. This argument is optional and by default is 10.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `recipes`: A list of [`Recipe`](#recipe) objects.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.

### Global Ingredient Info
#### Get Ingredient Info
`GET /api/ingredient-info/get` - Returns a JSON object containing the ingredient information for the ingredient with the specified ID.

Args
- `id (int)`: The ID of the target ingredient.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `ingredient`: An [`Ingredient`](#ingredient) object.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.
- 2 - No ingredient exists with the provided ID.

#### Search for Ingredients
`GET /api/ingredient-info/search` - Returns a list of ingredients which match the specified search query.

Args
- `query (str)`: The search query to use.
- `intolerances (list[str])`: The list of intolerances to use as a filter. This argument is optional.
- `sort_by (str)`: The criteria to use to sort the results. This argument is optional.
- `offset (int)`: The offset into the results to start at. This argument is optional and by default is 0.
- `limit (int)`: The maximum number of results to return. This argument is optional and by default is 10.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `ingredients`: A list of [`Ingredient`](#ingredient) objects.
- `total_results`: An integer describing the maximum number of available results.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.

### User-Saved Recipes
#### Get User Recipes
`GET /api/user-recipes/get` - Returns a list of recipe objects which the current user has saved.

Args
- `offset (int)`: The offset into the list to start at. This value must be greater than or equal to 0 and is optional (by default, it is 0).
- `limit (int)`: The maximum number of recipes to return. This value must be greater than or equal to 0 and is optional (by default, it is 0, which tells the server to return all of the current user's recipes).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `recipes`: A list of [`Recipe`](#recipe) objects. This list will be empty if the user has no saved recipes.
- `total_recipes (int)`: A value describing the total amount of recipes the current user has.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

#### Add User Recipe
`POST /api/user-recipes/add` - Adds the specified recipe to the current user's list of saved recipes.

Args
- `recipe`: The recipe to save, which must be a [`Recipe`](#recipe) object (the `summary` and `full_summary` fields are optional).

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The user already has the specified recipe.

#### Delete User Recipe
`POST /api/user-recipes/delete` - Deletes the specified recipe from the current user's list of saved recipes.

Args
- `id (int)`: The ID of the recipe to delete.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The user does not have the specified recipe.

#### Get Top User Recipes
`GET /api/user-recipes/get-top` - Returns a list of a random selection from the current user's most recently liked recipes.

The algorithm will look at only the most recently liked recipes and will only retrieve up to the specified limit of recipes.

Args
- `limit (int)`: The maximum number of recipes to return. This value must be greater than or equal to 0 and is optional (by default, the limit is 5).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `recipes`: A list of [`Recipe`](#recipe) objects. This list is guaranteed to be less than or equal to the specified limit.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

#### Get Top Friend Recipes
`GET /api/user-recipes/get-friend-top` - Returns a list of user/recipe list pairs generated based off of the liked recipes of the current user's friends.

The algorithm will look at only the most recently liked recipes and will only retrieve up to the specified limit of recipes per friend.

Args
- `friend_limit (int)`: The maximum amount of friends to sample from. This value must be greater than or equal to 0 and is optional (by default, the limit is 5).
- `limit_per_friend (int)`: The maximum amount of recipes to retrieve per friend. This value must be greater than or equal to 0 and is optional (by default, the limit is 5).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `friends`: A list of objects containing the following fields:
  - `friend`: A [`User`](#user) object describing the associated friend.
  - `recipes`: A list of [`Recipe`](#recipe) objects representing the friend's top recipes.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

#### Get Recommended Recipes
`GET /api/user-recipes/get-recommended` - Returns a list of recipe objects based on calculated recommendations for the current user.

This endpoint employs a set of algorithms to determine which recipes to retrieve and from where. These include:
- Based on recently liked: Chooses similar recipes to the user's most recently like recipes.
- What the user's friends like: Chooses recipes from the most recently liked recipes of a subset of the user's friends.
- Based on what the user's friends like: Chooses similar recipes to the most recently liked recipes from a subset of the user's friends.
- Based on liked ingredients: Chooses recipes that include the user's most recently liked ingredients.
- Random: Chooses recipes at random (the same as calling [`/api/recipe-info/get-random`](#get-random-recipes)).

Args
- `sources (list[str])`: The list of sources from which the algorithm should generate recipes. This argument is optional and can contain one or more of the following strings:
  - `recently_liked`: Chooses similar recipes to the user's most recently liked recipes.
  - `friends`: Chooses recipes from the most recently liked recipes of a subset of the user's friends.
  - `friends_similar`: Chooses similar recipes to the most recently liked recipes from a subset of the user's friends.
  - `ingredients`: Chooses recipes that include the user's most recently liked ingredients.
  - `random`: Chooses recipes at random (the same as calling [`/api/recipe-info/get-random`](#get-random-recipes)).
- `distributions (list[int])`: The list of distributions for the amount of recipes that should be generated per source. This argument is optional and if present, the number of elements in this list must equal the number of elements in `sources`. If the limit is defined as -1, each distribution is an exact limit per source. Otherwise, each distribution represents a percentage of the overall limit.
- `limit (int)`: The maximum number of recipes to return. This value is optional and is 10 by default. If the `distributions` list is also defined, then each distribution in the list represents a percentage of this value.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `recipes`: A list of [`Recipe`](#recipe) objects. This list will be empty if the algorithm was unable to retrieve any recipes for the specified sources and distributions.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

### User-Saved Ingredients
#### Get User Ingredients
`GET /api/user-ingredients/get` - Returns a list of ingredient objects which the current user has saved.

Args
- `offset (int)`: The offset into the list to start at. This value must be greater than or equal to 0 and is optional (by default, it is 0).
- `limit (int)`: The maximum number of ingredients to return. This value must be greater than or equal to 0 and is optional (by default, it is 0, which tells the server to return all of the current user's ingredients).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `ingredients`: A list of [`Ingredient`](#ingredient) objects. This list will be empty if the user has no saved ingredients.
- `total_ingredients (int)`: A value describing the total amount of ingredients the current user has.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

#### Add User Ingredient
`POST /api/user-ingredients/add` - Adds the specified ingredient to the current user's list of saved ingredients.

Args
- `ingredient`: The ingredient to save, which must be an [`Ingredient`](#ingredient) object.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The user already has the specified ingredient.

#### Delete User Ingredient
`POST /api/user-ingredients/delete` - Deletes the specified ingredient from the current user's list of saved ingredients.

Args
- `id (int)`: The ID of the ingredient to delete.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The user does not have the specified ingredient.

#### Get Top User Ingredients
`GET /api/user-ingredients/get-top` - Returns a list of a random selection from the current user's most recently liked ingredients.

The algorithm will look at only the most recently liked ingredients and will only retrieve up to the specified limit of ingredients.

Args
- `limit (int)`: The maximum number of ingredients to return. This value must be greater than or equal to 0 and is optional (by default, the limit is 5).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `ingredients`: A list of [`Ingredient`](#ingredient) objects. This list is guaranteed to be less than or equal to the specified limit.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

#### Get Top Friend Ingredients
`GET /api/user-ingredients/get-friend-top` - Returns a list of user/ingredient list pairs generated based off of the liked ingredients of the current user's friends.

The algorithm will look at only the most recently liked ingredients and will only retrieve up to the specified limit of ingredients per friend.

Args
- `friend_limit (int)`: The maximum amount of friends to sample from. This value must be greater than or equal to 0 and is optional (by default, the limit is 5).
- `limit_per_friend (int)`: The maximum amount of ingredients to retrieve per friend. This value must be greater than or equal to 0 and is optional (by default, the limit is 5).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `friends`: A list of objects containing the following fields:
  - `friend`: A [`User`](#user) object describing the associated friend.
  - `ingredients`: A list of [`Ingredient`](#ingredient) objects representing the friend's top ingredients.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

### Friends
#### Get Friends
`GET /api/friends/get` - Returns a list of the current user's friends.

Args
- `offset (int)`: The offset into the list to start at. This value must be greater than or equal to 0 and is optional (by default, it is 0).
- `limit (int)`: The maximum number of friends to return. This value must be greater than or equal to 0 and is optional (by default, it is 0, which tells the server to return all of the current user's friends).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `friends`: A list of [`User`](#user) objects representing the current user's friends.
- `total_friends (int)`: A value describing the total amount of friends the current user has.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

#### Send a Friend Request
`POST /api/friends/send-request` - Sends a friend request from the current user to the target user.

Args
- `target (str)`: The ID of the user to receive the request.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The user has already sent the request.

#### Handle a Friend Request
`POST /api/friends/handle-request` - Processes the request for the current user and the specified source user.

Args
- `src (str)`: The ID of the user who sent the request.
- `action (int)`: The action to perform, which must be one of:
  - 0 - Deny the request. If this action is performed, the friend request will be deleted automatically.
  - 1 - Accept the request. If this action is performed, a relationship between the two users will be added and the friend request will be deleted.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The user has no friend request from the specified source user.
- 4 - The specified source user does not exist.
- 5 - The specified action is invalid.

#### Get Sent Requests
`GET /api/friends/get-sent-requests` - Returns a list of users that have received friend requests from the current user.

Args
- `offset (int)`: The offset into the list to start at. This value must be greater than or equal to 0 and is optional (by default, it is 0).
- `limit (int)`: The maximum number of users to return. This value must be greater than or equal to 0 and is optional (by default, it is 0, which tells the server to return all of the sent requests).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `targets`: A list of [`User`](#user) objects representing the users which have received friend requests from the current user.
- `total_sent (int)`: A value describing the total amount of friend requests the current user has sent.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

#### Get Received Requests
`GET /api/friends/get-received-requests` - Returns a list of users that have sent friend requests to the current user.

Args
- `offset (int)`: The offset into the list to start at. This value must be greater than or equal to 0 and is optional (by default, it is 0).
- `limit (int)`: The maximum number of users to return. This value must be greater than or equal to 0 and is optional (by default, it is 0, which tells the server to return all of the received requests).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `sources`: A list of [`User`](#user) objects representing the users which have sent friend requests to the current user.
- `total_received (int)`: A value describing the total amount of friend requests the current user has received.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

### User Intolerances
#### Get User Intolerances
`GET /api/user-intolerances/get` - Returns a list of intolerances the current user has saved.

Args
- `offset (int)`: The offset into the list to start at. This value must be greater than or equal to 0 and is optional (by default, it is 0).
- `limit (int)`: The maximum number of intolerances to return. This value must be greater than or equal to 0 and is optional (by default, it is 0, which tells the server to return all of the current user's saved intolerances).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `intolerances`: A list of [`Intolerance`](#intolerance) objects representing the intolerances the current user has saved.
- `total_intolerances (int)`: A value describing the total amount of intolerances the current user has.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.

#### Add User Intolerance
`POST /api/user-intolerances/add` - Adds the specified intolerance to the current user's list of saved intolerances.

Args
- `id (int)`: The ID of the intolerance to add.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The specified intolerance is invalid.
- 4 - The user already has the specified intolerance.


#### Delete User Intolerance
`POST /api/user-intolerances/delete` - Deletes the specified intolerance from the current user's list of saved intolerances.

Args
- `id (int)`: The ID of the intolerance to delete.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The specified intolerance is invalid.
- 4 - The user does not have the specified intolerance.

### Users
#### Search for Users
`GET /api/users/search` - Returns a list of users which match the specified query string.

Args
- `query (str)`: The query string to use.
- `search_by (str)`: The field to search by. This must be one of:
  - `username`: The user's username.
  - `full_name`: The user's given and family name.
  - `given_name`: The user's given name.
  - `family_name`: The user's family name.
- `offset (int)`: The offset into the search results to start at. This value must be greater than or equal to 0 and is optional (by default, it is 0).
- `limit (int)`: The maximum number of users to return. This value must be greater than or equal to 0 and is optional (by default, it is 10).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `results`: A list of [`User`](#user) objects representing the search results.
- `total_results (int)`: A value describing the total amount of search results for the given query.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.

#### Get a User
`GET /api/users/get` - Returns information describing the specified user.

Args
- `query (str)`: The query to use.
- `by (str)`: The field by which the user should be retrieved. This must be one of:
  - `id`: Get a user by their ID.
  - `username`: Get a user by their username.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `user`: A [`User`](#user) object.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.
- 2 - No user exists which matches the provided query.
- 3 - The specified `by` condition is invalid.

### Account Info
#### Update Account Info
`POST /api/account/update` - Updates the current user's account according to the provided information.

All arguments to this endpoint are optional.

Args
- `email (str)`: The user's email.
- `username (str)`: The user's username.
- `given_name (str)`: The user's given name.
- `family_name (str)`: The user's family name.
- `profile_image (str)`: The user's profile image.
- `profile_visibility (int)`: The user's profile visibility.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - One or more of the input arguments contain invalid syntax.
- 3 - The specified email and/or username was already taken.

#### Update Password
`POST /api/account/update-password` - Updates the current user's password.

This endpoint only applies to users whose authentication method is `DEFAULT` (i.e. users who have an account directly through PieceMeal).

The arguments to this endpoint must be encrypted using the server's public key, which can be obtained using the [`/api/key/get`](#get-server-public-key) endpoint.

Args
- `old_password (str)`: The user's current password.
- `new_password (str)`: The new password to use.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.
- 2 - The input arguments were missing or otherwise corrupted.
- 3 - The old password was invalid.

#### Delete Account
`POST /api/account/delete` - Deletes the current user's account and invalidates the session.

Returns

On success, a JSON object containing the following field:
- `success (bool)`: Whether the request was successfully completed.

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - There is no user currently logged in.

### Miscellaneous
#### Get Server Public Key
`GET /api/key/get` - Returns the server's public key used to encrypt certain requests made to the server.

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `key (str)`: The server's public key.

On failure, the possible error codes are:
- 0 - A general exception occurred.

#### Initiate Login Flow
`POST /api/login/init` - Initiates the login flow.

The arguments to this endpoint must be encrypted using the server's public key, which can be obtained using the [`/api/key/get`](#get-server-public-key) endpoint.

On success, the specified user will be logged in.

Args
- `authentication (int)`: The authentication method to use.
- `username (str)`: The target user's username. This value is only required if the authentication method is `DEFAULT` (0).
- `password (str)`: The target user's password. This value is only required if the authentication method is `DEFAULT` (0).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `redirect_url (str)`: The redirect URL which should handle the external login. This value is only present if the authentication method is `GOOGLE` (1).

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.
- 2 - The provided authentication method is invalid.
- 3 - The provided username or password is invalid.


#### Initiate Signup Flow
`POST /api/signup/init` - Initiates the signup flow.

The arguments to this endpoint must be encrypted using the server's public key, which can be obtained using the [`/api/key/get`](#get-server-public-key) endpoint.

On success, the specified user will be logged in.

Args
- `authentication (int)`: The authentication method to use.
- `username (str)`: The target user's username. This value is only required if the authentication method is `DEFAULT` (0).
- `email (str)`: The target user's email. This value is only required if the authentication method is `DEFAULT` (0).
- `password (str)`: The target user's password. This value is only required if the authentication method is `DEFAULT` (0).
- `given_name (str)`: The target user's given name. This value is only required if the authentication method is `DEFAULT` (0).
- `family_name (str)`: The target user's family name. This value is only required if the authentication method is `DEFAULT` (0).

Returns

On success, a JSON object containing the following fields:
- `success (bool)`: Whether the request was successfully completed.
- `redirect_url (str)`: The redirect URL which should handle the external login. This value is only present if the authentication method is `GOOGLE` (1).

On failure, the possible error codes are:
- 0 - A general exception occurred.
- 1 - The input arguments were missing or otherwise corrupted.
- 2 - The provided authentication method is invalid.
- 3 - One or more of the provided fields has invalid syntax.
- 4 - The specified username or email is already taken.