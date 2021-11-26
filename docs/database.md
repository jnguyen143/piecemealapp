# Database API
The following document details the database API calls and types.

## Table of Contents
- [Database API](#database-api)
  - [Table of Contents](#table-of-contents)
  - [Types](#types)
    - [`UserIntolerance`](#userintolerance)
    - [`UserAuthentication`](#userauthentication)
    - [`UserStatus`](#userstatus)
    - [`DatabaseException`](#databaseexception)
    - [`NoUserException`](#nouserexception)
    - [`NoRecipeException`](#norecipeexception)
    - [`NoIngredientException`](#noingredientexception)
    - [`DuplicateUserException`](#duplicateuserexception)
    - [`DuplicateRecipeException`](#duplicaterecipeexception)
    - [`DuplicateIngredientException`](#duplicateingredientexception)
    - [`InvalidArgumentException`](#invalidargumentexception)
    - [`EncryptionException`](#encryptionexception)
    - [`ProfileVisibility`](#profilevisibility)
  - [Tables](#tables)
    - [Users](#users)
    - [Recipes](#recipes)
    - [Ingredients](#ingredients)
    - [Saved Recipes](#saved-recipes)
    - [Saved Ingredients](#saved-ingredients)
    - [Intolerances](#intolerances)
    - [Passwords](#passwords)
    - [Friends](#friends)
    - [Friend Requests](#friend-requests)
  - [Functions](#functions)
    - [User Management](#user-management)
      - [Add User](#add-user)
      - [Get User by ID](#get-user-by-id)
      - [Get User by Username](#get-user-by-username)
      - [Delete User](#delete-user)
      - [User Exists](#user-exists)
      - [Add Multiple Users](#add-multiple-users)
      - [Get Multiple Users by ID](#get-multiple-users-by-id)
      - [Get Multiple Users by Username](#get-multiple-users-by-username)
      - [Delete Multiple Users](#delete-multiple-users)
      - [Search Users by Name](#search-users-by-name)
      - [Search Users by Username](#search-users-by-username)
    - [Global Recipe Info](#global-recipe-info)
      - [Add Recipe Info](#add-recipe-info)
      - [Get Recipe Info](#get-recipe-info)
      - [Delete Recipe Info](#delete-recipe-info)
      - [Recipe Info Exists](#recipe-info-exists)
      - [Add Multiple Recipe Infos](#add-multiple-recipe-infos)
      - [Get Multiple Recipe Infos](#get-multiple-recipe-infos)
      - [Delete Multiple Recipe Infos](#delete-multiple-recipe-infos)
      - [Get Random Recipe Infos](#get-random-recipe-infos)
    - [Global Ingredient Info](#global-ingredient-info)
      - [Add Ingredient Info](#add-ingredient-info)
      - [Get Ingredient Info](#get-ingredient-info)
      - [Delete Ingredient Info](#delete-ingredient-info)
      - [Ingredient Info Exists](#ingredient-info-exists)
      - [Add Multiple Ingredient Infos](#add-multiple-ingredient-infos)
      - [Get Multiple Ingredient Infos](#get-multiple-ingredient-infos)
      - [Delete Multiple Ingredient Infos](#delete-multiple-ingredient-infos)
    - [Friends](#friends-1)
      - [Add Relationship](#add-relationship)
      - [Has Relationship](#has-relationship)
      - [Delete Relationship](#delete-relationship)
      - [Get Relationships for User](#get-relationships-for-user)
      - [Add Friend Request](#add-friend-request)
      - [Get Friend Requests for Source](#get-friend-requests-for-source)
      - [Get Friend Requests for Target](#get-friend-requests-for-target)
      - [Delete Friend Request](#delete-friend-request)
    - [User Intolerances](#user-intolerances)
      - [Add Intolerance](#add-intolerance)
      - [Has Intolerance](#has-intolerance)
      - [Delete Intolerance](#delete-intolerance)
      - [Get Intolerances](#get-intolerances)
    - [User-Saved Recipes](#user-saved-recipes)
      - [Add Recipe](#add-recipe)
      - [Has Recipe](#has-recipe)
      - [Delete Recipe](#delete-recipe)
      - [Get Recipes](#get-recipes)
      - [Add Multiple Recipes](#add-multiple-recipes)
      - [Delete Multiple Recipes](#delete-multiple-recipes)
      - [Get User Top Recipes](#get-user-top-recipes)
      - [Get Friend Top Recipes](#get-friend-top-recipes)
    - [User-Saved Ingredients](#user-saved-ingredients)
      - [Add Ingredient](#add-ingredient)
      - [Has Ingredient](#has-ingredient)
      - [Delete Ingredient](#delete-ingredient)
      - [Get Ingredients](#get-ingredients)
      - [Add Multiple Ingredients](#add-multiple-ingredients)
      - [Delete Multiple Ingredients](#delete-multiple-ingredients)
      - [Get User Top Ingredients](#get-user-top-ingredients)
      - [Get Friend Top Ingredients](#get-friend-top-ingredients)
    - [User Account Management](#user-account-management)
      - [Set Username](#set-username)
      - [Set Email](#set-email)
      - [Set Password](#set-password)
      - [Validate Password](#validate-password)
      - [Set Profile Image](#set-profile-image)
      - [Set User Status](#set-user-status)
      - [Set Name](#set-name)
      - [Set Given Name](#set-given-name)
      - [Set Family Name](#set-family-name)
      - [Set Profile Visibility](#set-profile-visibility)

## Types
### `UserIntolerance`
This type specifies the available intolerance types a user can have.

|     ID      | Integral Value | Details                                |
| :---------: | :------------: | -------------------------------------- |
|   `DAIRY`   |       0        | Any intolerance to dairy products.     |
|    `EGG`    |       1        | Any intolerance to egg products.       |
|  `GLUTEN`   |       2        | Any intolerance to gluten products.    |
|   `GRAIN`   |       3        | Any intolerance to grain products.     |
|  `PEANUT`   |       4        | Any intolerance to peanut products.    |
|  `SEAFOOD`  |       5        | Any intolerance to seafood products.   |
|  `SESAME`   |       6        | Any intolerance to sesame products.    |
| `SHELLFISH` |       7        | Any intolerance to shellfish products. |
|    `SOY`    |       8        | Any intolerance to soy products.       |
|  `SULFITE`  |       9        | Any intolerance to sulfite products.   |
| `TREE_NUT`  |       10       | Any intolerance to tree nut products.  |
|   `WHEAT`   |       11       | Any intolerance to wheat products.     |

### `UserAuthentication`
This type specifies all of the possible methods a user can use to authorize themselves.

|    ID     | Integral Value | Details                                                                              |
| :-------: | :------------: | ------------------------------------------------------------------------------------ |
| `DEFAULT` |       0        | Default authentication. Users with this method authorize directly through PieceMeal. |
| `GOOGLE`  |       1        | Google authentication. Users with this method authorize externally through Google.   |

### `UserStatus`
This type specifies all of the possible statuses a user can have.

|      ID       | Integral Value | Details                                                                                                                                                                                                                             |
| :-----------: | :------------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `UNVERIFIED`  |       0        | An unverified user. Users with this status cannot log in until they verify their account.                                                                                                                                           |
|  `VERIFIED`   |       1        | A verified user. Users with this status can log in as normal and perform any functions that a normal user should be able to perform.                                                                                                |
| `DEACTIVATED` |       2        | A deactivated user. Users with this status cannot log in unless a system administrator changes their status manually. This status is here for when a user needs to be prevented from logging in, but not deleted from the database. |

### `DatabaseException`
Raised when there is a general problem during a database access.

### `NoUserException`
Raised when the specified ID or username does not correspond to any user in the database.

### `NoRecipeException`
Raised when the specified ID does not correspond to any recipe in the database.

### `NoIngredientException`
Raised when the specified ID does not correspond to any ingredient in the database.

### `DuplicateUserException`
Raised when the specified ID, username, or email already corresponds to a user in the database.

### `DuplicateRecipeException`
Raised when the specified ID already corresponds to a recipe in the database.

### `DuplicateIngredientException`
Raised when the specified ID already corresponds to an ingredient in the database.

### `InvalidArgumentException`
Raised when an argument to a database-related function is invalid.

### `EncryptionException`
Raised when there is a problem ensuring the integrity of an encrypted piece of data in a database call.

### `ProfileVisibility`
This type specifies all of the possible values for the `profile_visibility` field in the `users` table.

The `profile_visibility` field is a _bitfield_ value. This means that the profile visibility may have zero or more of any combination of the values in the table below.

To check if the profile visibility has a particular value, use `ProfileVisibility.has(bitfield, value)`, which checks if the specified profile visibility bitfield has the specified `ProfileVisibility` value.

To enable a value in the profile visibility, use `bitfield = ProfileVisibility.enable(bitfield, value)`, which will set the `value` bit in the `bitfield` variable to 1 (true).

To disable a value in the profile visibility, use `bitfield = ProfileVisibility.disable(bitfield, value)`, which will set the `value` bit in the `bitfield` variable to 0 (false).

To enable all values in the profile visibility, use `bitfield = ProfileVisibility.enable_all()`. To disable all values in the profile visibility, use `bitfield = ProfileVisibility.disable_all()`.

|         ID          | Integral Value | Details                                                                  |
| :-----------------: | :------------: | ------------------------------------------------------------------------ |
|       `NAME`        |     `0x01`     | Determines if the user's given and family name will be publicly visible. |
|   `CREATION_DATE`   |     `0x02`     | Determines if the user's account creation date will be publicly visible. |
|   `INTOLERANCES`    |     `0x04`     | Determines if the user's saved intolerances will be publicly visible.    |
|   `SAVED_RECIPES`   |     `0x08`     | Determines if the user's saved recipes will be publicly visible.         |
| `SAVED_INGREDIENTS` |     `0x10`     | Determines if the user's saved ingredients will be publicly visible.     |
|      `FRIENDS`      |     `0x20`     | Determines if the user's friend list will be publicly visible.           |

## Tables
### Users
The `users` table is responsible for storing user data. It keeps track of all users across the site and their related account information, such as their IDs, usernames, emails, and authentication methods.

The following table details the columns in the `users` table:
|     Column Name      |      Type      | Details                                                                                                                                                                                                                                                                                       |
| :------------------: | :------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|         `id`         | `varchar(255)` | The ID of the user. This value is unique across all users, must be less than or equal to 255 characters in length, and can only contain ASCII-compatible characters.                                                                                                                          |
|      `username`      | `varchar(50)`  | The username of the user. This value is unique across all users and must be between 3 and 50 characters in length. Usernames can only contain uppercase and lowercase regular Latin letters, Arabic numerals, hyphens, underscores, periods, and US dollar signs.                             |
|       `email`        | `varchar(255)` | The user's email. This value is unique across all users and must be less than or equal to 255 characters in length.                                                                                                                                                                           |
|     `given_name`     | `varchar(255)` | The user's given name. This value must be less than or equal to 255 characters in length.                                                                                                                                                                                                     |
|    `family_name`     | `varchar(255)` | The user's family name. This value must be less than or equal to 255 characters in length.                                                                                                                                                                                                    |
|   `profile_image`    |     `text`     | The URL for the user's profile image.                                                                                                                                                                                                                                                         |
|   `creation_date`    |  `timestamp`   | The time at which the user's account was created.                                                                                                                                                                                                                                             |
|   `authentication`   |     `int`      | The authentication method for the user. This value must be one of the values specified by `UserAuthentication`.                                                                                                                                                                               |
|       `status`       |     `int`      | The user's status. This value must be one of the values specified by `UserStatus`.                                                                                                                                                                                                            |
| `profile_visibility` |     `int`      | The user's profile visibility. This value determines what other users who are not friends with the user can see on their profile page. This value is a bitfield which must be made up of any combination of the values specified by `ProfileVisibility`. By default, all fields are disabled. |

The following code snippet details the exact function used to create the `users` table:
```sql
CREATE TABLE users (
    id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    given_name VARCHAR(255),
    family_name VARCHAR(255),
    profile_image TEXT DEFAULT '/static/default_user_profile_image.png',
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    authentication INT NOT NULL,
    status INT NOT NULL DEFAULT 0,
    profile_visibility INT NOT NULL DEFAULT 0,
    PRIMARY KEY (id)
);
```

### Recipes
The `recipes` table is responsible for storing global information of recipes across the site without reference to any users. This table is designed to be used as a central location to retrieve information about recipes without having to resort to making calls to 3rd party APIs every time a request for recipe information needs to be made.

Keep in mind this table stores _global_ information. This means that it does not store information associated with any particular user. For storing recipes with particular users, refer to the `saved_recipes` table.

The following table details the columns in the `recipes` table:
|  Column Name   |      Type      | Details                                                                                                         |
| :------------: | :------------: | --------------------------------------------------------------------------------------------------------------- |
|      `id`      |     `int`      | The ID of the recipe. This value is unique across all recipes and is the same ID used in Spoonacular API calls. |
|     `name`     | `varchar(255)` | The name of the recipe.                                                                                         |
|    `image`     |     `text`     | The URL for the recipe's image.                                                                                 |
|   `summary`    |     `text`     | The (brief) summary for the recipe.                                                                             |
| `full_summary` |     `text`     | The full summary for the recipe.                                                                                |

The following code snippet details the exact function used to create the `recipes` table:
```sql
CREATE TABLE recipes (
    id INT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    image TEXT,
    summary TEXT,
    full_summary TEXT,
    PRIMARY KEY (id)
);
```

### Ingredients
The `ingredients` table is responsible for storing global information of ingredients across the site without reference to any users. This table is designed to be used as a central location to retrieve information about ingredients without having to resort to making calls to 3rd party APIs every time a request for ingredient information needs to be made.

Keep in mind this table stores _global_ information. This means that it does not store information associated with any particular user. For storing ingredients with particular users, refer to the `saved_ingredients` table.

The following table details the columns in the `ingredients` table:
| Column Name |      Type      | Details                                                                                                                |
| :---------: | :------------: | ---------------------------------------------------------------------------------------------------------------------- |
|    `id`     |     `int`      | The ID of the ingredient. This value is unique across all ingredient and is the same ID used in Spoonacular API calls. |
|   `name`    | `varchar(255)` | The name of the ingredient.                                                                                            |
|   `image`   |     `text`     | The URL for the ingredient's image.                                                                                    |

The following code snippet details the exact function used to create the `ingredients` table:
```sql
CREATE TABLE ingredients (
    id INT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    image TEXT,
    PRIMARY KEY (id)
);
```

### Saved Recipes
The `saved_recipes` table is responsible for storing information about a user's saved recipes. This table only stores mappings for users to recipes; it does *not* store actual user or recipe information. To retrieve user and recipe information, refer to the `users` and `recipes` tables, respectively.

The following table details the columns in the `saved_recipes` table:
| Column Name |      Type      | Details                                                            |
| :---------: | :------------: | ------------------------------------------------------------------ |
|    `id`     |     `int`      | The ID of the saved recipe. This value is automatically generated. |
|  `user_id`  | `varchar(255)` | The ID of the associated user.                                     |
| `recipe_id` |     `int`      | The ID of the associated recipe.                                   |

The following code snippet details the exact function used to create the `saved_recipes` table:
```sql
CREATE TABLE saved_recipes (
    id INT UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY,
    user_id VARCHAR(255) NOT NULL,
    recipe_id INT,
    PRIMARY KEY (id),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_recipe FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON UPDATE CASCADE ON DELETE SET NULL
);
```

### Saved Ingredients
The `saved_ingredients` table is responsible for storing information about a user's saved ingredients. This table only stores mappings for users to ingredients; it does *not* store actual user or ingredient information. To retrieve user and ingredient information, refer to the `users` and `ingredients` tables, respectively.

The following table details the columns in the `saved_ingredients` table:
|   Column Name   |      Type      | Details                                                                |
| :-------------: | :------------: | ---------------------------------------------------------------------- |
|      `id`       |     `int`      | The ID of the saved ingredient. This value is automatically generated. |
|    `user_id`    | `varchar(255)` | The ID of the associated user.                                         |
| `ingredient_id` |     `int`      | The ID of the associated ingredient.                                   |

The following code snippet details the exact function used to create the `saved_ingredients` table:
```sql
CREATE TABLE saved_ingredients (
    id INT UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY,
    user_id VARCHAR(255) NOT NULL,
    ingredient_id INT,
    PRIMARY KEY (id),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_ingredient FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON UPDATE CASCADE ON DELETE SET NULL
);
```

### Intolerances
The `intolerances` table is used to store information about a user's selected intolerances. Intolerance information is used to determine and restrict which recipes and ingredients a user sees.

The following table details the columns in the `intolerances` table:
|  Column Name  |      Type      | Details                                                                                                   |
| :-----------: | :------------: | --------------------------------------------------------------------------------------------------------- |
|     `id`      |     `int`      | The ID of the intolerance entry. This value is automatically generated.                                   |
|   `user_id`   | `varchar(255)` | The ID of the associated user.                                                                            |
| `intolerance` |     `int`      | The associated intolerance. This value must be one of the values specified by the `UserIntolerance` type. |

The following code snippet details the exact function used to create the `intolerance` table:
```sql
CREATE TABLE intolerances (
    id INT UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY,
    user_id VARCHAR(255) NOT NULL,
    intolerance INT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);
```

### Passwords
The `passwords` table stores passwords for all users with `DEFAULT` authentication. Passwords stored in this table are salted and encrypted.

The following table details the columns in the `passwords` table:
| Column Name |      Type      | Details                                                              |
| :---------: | :------------: | -------------------------------------------------------------------- |
|    `id`     |     `int`      | The ID of the password entry. This value is automatically generated. |
|  `user_id`  | `varchar(255)` | The ID of the associated user.                                       |
|  `phrase`   |     `text`     | The encrypted password phrase.                                       |

The following code snippet details the exact function used to create the `passwords` table:
```sql
CREATE TABLE passwords (
    id INT UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY,
    user_id VARCHAR(255) NOT NULL,
    phrase TEXT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);
```

### Friends
The `friends` table is used to store relationship information between users. It does not store actual user data. To retrieve user information, refer to the `users` table.

The following table details the columns in the `friends` table:
| Column Name |      Type      | Details                                                              |
| :---------: | :------------: | -------------------------------------------------------------------- |
|    `id`     |     `int`      | The ID of the relation entry. This value is automatically generated. |
|   `user1`   | `varchar(255)` | The ID of the first user in the relation entry.                      |
|   `user2`   | `varchar(255)` | The ID of the second user in the relation entry.                     |

The following code snippet details the exact function used to create the `friends` table:
```sql
CREATE TABLE friends (
    id INT UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY,
    user1 VARCHAR(255) NOT NULL,
    user2 VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_user1 FOREIGN KEY (user1) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_user2 FOREIGN KEY (user2) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);
```

### Friend Requests
The `friend_requests` table is used to store friend requests. If the request is confirmed, a new entry in the `friends` table is created. Otherwise, the friend request is simply deleted.

The following table details the columns in the `friend_requests` table:
| Column Name |      Type      | Details                                                                                      |
| :---------: | :------------: | -------------------------------------------------------------------------------------------- |
|    `id`     |     `int`      | The ID of the request entry. This value is automatically generated.                          |
|    `src`    | `varchar(255)` | The ID of the source user (i.e. the user who made the request) in the request entry.         |
|  `target`   | `varchar(255)` | The ID of the target user (i.e. the user who is receiving the request) in the request entry. |

The following code snippet details the exact function used to create the `friend_requests` table:
```sql
CREATE TABLE friends (
    id INT UNIQUE NOT NULL GENERATED ALWAYS AS IDENTITY,
    src VARCHAR(255) NOT NULL,
    target VARCHAR(255) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_src FOREIGN KEY (src) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_target FOREIGN KEY (target) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE
);
```

## Functions

### User Management
#### Add User
`add_user(userdata: dict)` - Creates a new user with the specified user data.

Args
- `userdata (dict)`: A dictionary of user data values consisting of the following entries (required entries are listed first):

|         Key          | Type  | Usage                                                                                                                                                                                                                                                    | Required |
| :------------------: | :---: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------: |
|   `authentication`   | `int` | The authentication type for the user. This value must be one of the values specified by the `UserAuthentication` type.                                                                                                                                   |   Yes    |
|       `email`        | `str` | The user's email. This value must be unique across all users and is checked for syntax correctness.                                                                                                                                                      |   Yes    |
|      `password`      | `str` | The user's (unencrypted) password. This value is only required for accounts whose authentication method is `DEFAULT`.                                                                                                                                    |   No*    |
|         `id`         | `str` | The internal ID of the user. This value must be unique across all users. If it is not present, this function will automatically generate a value.                                                                                                        |    No    |
|      `username`      | `str` | The username of the user. This value must be unique across all users. If it is not present, this function will automatically generate a value.                                                                                                           |    No    |
|     `given_name`     | `str` | The user's given name.                                                                                                                                                                                                                                   |    No    |
|    `family_name`     | `str` | The user's family name.                                                                                                                                                                                                                                  |    No    |
|   `profile_image`    | `str` | The URL for the user's profile image. If it is not present, this function will automatically insert a default URL.                                                                                                                                       |    No    |
|       `status`       | `int` | The user's status. This must be one of the values specified by the `UserStatus` type. If it is not present, this function will automatically assign a status of `UNVERIFIED` (due to the email having not yet been verified).                            |    No    |
| `profile_visibility` | `int` | The user's profile visibility. The user's profile visibility. This must be a bitfield containing the values specified by the `ProfileVisibility` type. If it is not present, this function will automatically assign a value of 0 (all fields disabled). |

Raises
- `DatabaseException`: If the function failed to create the user.
- `DuplicateUserException`: If a user already exists in the database with the specified ID, username, or email.
- `InvalidArgumentException`: If any of the provided arguments were invalid.
- `EncryptionException`: If the authentication method is `DEFAULT` and the provided password was unable to be properly encrypted.

#### Get User by ID
`get_user_by_id(user_id: str) -> User` - Returns the `User` object whose ID matches the provided value.

Args
- `user_id (str)`: The ID of the target user.

Returns

The `User` object of the target user.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoUserException`: If the passed ID does not correspond to any user in the database.

#### Get User by Username
`get_user_by_username(username: str) -> User` - Returns the `User` object whose username matches the provided value.

Args
- `username (str)`: The username of the target user.

Returns

The `User` object of the target user.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoUserException`: If the passed username does not correspond to any user in the database.

#### Delete User
`delete_user(user_id: str)` - Deletes the user with the specified ID.

Args
- `user_id (str)`: The ID of the target user.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoUserException`: If the passed ID does not correspond to any user in the database.

#### User Exists
`user_exists(user_id: str) -> bool` - Returns true if a user exists with the specified ID.

Args
- `user_id (str)`: The ID of the target user.

Returns

True if the user exists and false otherwise.

Raises
- `DatabaseException`: If the function failed to query the database.

#### Add Multiple Users
`add_users(userdata: list[dict])` - Creates new users with the specified user data.

This is a bulk operation, which means it is equivalent to calling `add_user()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `userdata (list[dict])`: The list of userdata dictionaries to use to create the users. The format of the dictionaries is specified under [`add_user()`](#add-user).

Raises
- `DatabaseException`: If the function failed to create the users.
- `DuplicateUserException`: If a user already exists in the database with any of the the specified IDs, usernames, or emails.
- `InvalidArgumentException`: If any of the provided arguments were invalid.
- `EncryptionException`: If the authentication method for any of the users is `DEFAULT` and the provided password was unable to be properly encrypted.

#### Get Multiple Users by ID
`get_users_by_id(user_ids: list[str]) -> list[User]` - Returns a list of `User` objects whose IDs match the specified user IDs.

This is a bulk operation, which means it is equivalent to calling `get_user_by_id()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `user_ids (list[str])`: The IDs of the target users.

Returns

A list of `User` objects whose IDs match the specified user IDs.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoUserException`: If any of the passed IDs do not correspond to a user in the database. 

#### Get Multiple Users by Username
`get_users_by_username(usernames: list[str]) -> list[User]` - Returns a list of `User` objects whose usernames match the specified usernames.

This is a bulk operation, which means it is equivalent to calling `get_user_by_username()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `usernames (list[str])`: The usernames of the target users.

Returns

A list of `User` objects whose usernames match the specified usernames.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoUserException`: If any of the passed usernames do not correspond to a user in the database.

#### Delete Multiple Users
`delete_users(user_ids: list[str])` - Deletes all of the users with the specified user IDs.

This is a bulk operation, which means it is equivalent to calling `delete_user()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `user_ids (list[str])`: The IDs of the target users.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoUserException`: If any of the passed IDs do not correspond to a user in the database.

#### Search Users by Name
`search_users_by_name(query: str, offset: int = 0, limit: int = 10) -> (list[User], int)` - Returns a list of `User` objects whose names contain the given query string and the maximum number of available results.

Args
- `query (str)`: The query string to use when searching for users.
- `offset (int)`: The offset into the search results to start at. This value is optional and is 0 by default.
- `limit (int)`: The maximum number of users to return. This value is optional and is 10 by default.

Returns

A tuple containing the list of `User` objects whose names contain the given query string, or an empty list if no users match the query, and an integer describing the maximum number of available results.

Raises
- `DatabaseException`: If the function failed to query the database.
- `InvalidArgumentException`: If the specified offset or limit was less than 0.

#### Search Users by Username
`search_users_by_username(query: str, offset: int = 0, limit: int = 10) -> (list[User], int)` - Returns a list of `User` objects whose usernames contain the given query string and the maximum number of available results.

Args
- `query (str)`: The query string to use when searching for users.
- `offset (int)`: The offset into the search results to start at. This value is optional and is 0 by default.
- `limit (int)`: The maximum number of users to return. This value is optional and is 10 by default.

Returns

A tuple containing the list of User objects whose usernames contain the given query string, or an empty list if no users match the query, and an integer describing the maximum number of available results.

Raises
- `DatabaseException`: If the function failed to query the database.
- `InvalidArgumentException`: If the specified offset or limit was less than 0.

### Global Recipe Info
#### Add Recipe Info
`add_recipe_info(info: dict)` - Adds the recipe with the specified information to the database.

Args
- `info (dict)`: A dictionary of recipe info values consisting of the following entries (required entries are listed first):

|      Key       | Type  | Usage                                                                                                       | Required |
| :------------: | :---: | ----------------------------------------------------------------------------------------------------------- | :------: |
|      `id`      | `int` | The ID of the recipe.                                                                                       |   Yes    |
|     `name`     | `str` | The name of the recipe.                                                                                     |   Yes    |
|    `image`     | `str` | The URL of the recipe's image. If it is not present, this function will automatically insert a default URL. |    No    |
|   `summary`    | `str` | The (brief) summary for the recipe.                                                                         |    No    |
| `full_summary` | `str` | The full summary for the recipe.                                                                            |    No    |

Raises
- `DatabaseException`: If the function failed to add the recipe.
- `DuplicateRecipeException`: If a recipe already exists in the database with the specified ID.
- `InvalidArgumentException`: If any of the provided arguments were invalid.

#### Get Recipe Info
`get_recipe_info(recipe_id: int) -> Recipe` - Returns the `Recipe` object whose ID matches the provided ID.

Args
- `recipe_id (int)`: The ID of the target recipe.

Returns

The `Recipe` object whose ID matches the provided one.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoRecipeException`: If no recipe exists with the specified ID.

#### Delete Recipe Info
`delete_recipe_info(recipe_id: int)` - Deletes the recipe whose ID matches the provided ID.

Args
- `recipe_id (int)`: The ID of the target recipe.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoRecipeException`: If no recipe exists with the specified ID.

#### Recipe Info Exists
`recipe_info_exists(recipe_id: int) -> bool` - Returns true if a recipe with the specified ID exists in the database.

Args
- `recipe_id (int)`: The ID of the target recipe.

Returns

True if a recipe with the specified ID exists in the database and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.

#### Add Multiple Recipe Infos
`add_recipe_infos(infos: list[dict], ignore_duplicates: bool = False)` - Adds multiple recipes to the database whose data is specified in the list of recipe information.

This is a bulk operation, which means it is equivalent to calling `add_recipe_info()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `infos (list[dict])`: The list of recipe information dictionaries to use to create the recipes. The format of the dictionaries is specified under [`add_recipe_info()`](#add-recipe-info).
- `ignore_duplicates (bool)`: Whether this function should skip over duplicate recipes instead of raising an error. This value is optional and is false by default.

Raises
- `DatabaseException`: If the function failed to add the recipes.
- `DuplicateRecipeException`: If a recipe already exists in the database with any of the specified IDs.
- `InvalidArgumentException`: If any of the provided arguments were invalid.

#### Get Multiple Recipe Infos
`get_recipe_infos(recipe_ids: list[int]) -> list[Recipe]` - Returns a list of `Recipe` objects whose IDs match the specified recipe IDs.

This is a bulk operation, which means it is equivalent to calling `get_recipe_info()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `recipe_ids (list[int])`: The IDs of the target recipes.

Returns

A list of `Recipe` objects whose IDs match the specified recipe IDs.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoRecipeException`: If any of the passed IDs do not correspond to a recipe in the database.

#### Delete Multiple Recipe Infos
`delete_recipe_infos(recipe_ids: list[int])` - Deletes all of the recipes with the specified user IDs.

This is a bulk operation, which means it is equivalent to calling `delete_recipe_infos()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `recipe_ids (list[int])`: The IDs of the target recipes.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoRecipeException`: If any of the passed IDs do not correspond to a recipe in the database.

#### Get Random Recipe Infos
`get_random_recipe_infos(limit: int = 10) -> list[Recipe]` - Returns a random list of recipes.

Args
- `limit (int)`: The maximum number of results to return. This value is optional and is 10 by default.

Returns

A random list of `Recipe` objects, or an empty list if there are no recipe objects in the database.

Raises
- `DatabaseException`: If the function failed to query the database.
- `InvalidArgumentException`: If the specified limit was less than 1.

### Global Ingredient Info
#### Add Ingredient Info
`add_ingredient_info(info: dict)` - Adds the ingredient with the specified information to the database.

Args
- `info (dict)`: A dictionary of ingredient info values consisting of the following entries (required entries are listed first):

|   Key   | Type  | Usage                                                                                                           | Required |
| :-----: | :---: | --------------------------------------------------------------------------------------------------------------- | :------: |
|  `id`   | `int` | The ID of the ingredient.                                                                                       |   Yes    |
| `name`  | `str` | The name of the ingredient.                                                                                     |   Yes    |
| `image` | `str` | The URL of the ingredient's image. If it is not present, this function will automatically insert a default URL. |    No    |

Raises
- `DatabaseException`: If the function failed to add the ingredient.
- `DuplicateIngredientException`: If a ingredient already exists in the database with the specified ID.
- `InvalidArgumentException`: If any of the provided arguments were invalid.

#### Get Ingredient Info
`get_ingredient_info(ingredient_id: int) -> Ingredient` - Returns the `Ingredient` object whose ID matches the provided ID.

Args
- `ingredient_id (int)`: The ID of the target ingredient.

Returns

The `Ingredient` object whose ID matches the provided one.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoIngredientException`: If no ingredient exists with the specified ID.

#### Delete Ingredient Info
`delete_ingredient_info(ingredient_id: int)` - Deletes the ingredient whose ID matches the provided ID.

Args
- `ingredient_id (int)`: The ID of the target ingredient.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoIngredientException`: If no ingredient exists with the specified ID.

#### Ingredient Info Exists
`ingredient_info_exists(ingredient_id: int) -> bool` - Returns true if an ingredient with the specified ID exists in the database.

Args
- `ingredient_id (int)`: The ID of the target ingredient.

Returns

True if an ingredient with the specified ID exists in the database and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.

#### Add Multiple Ingredient Infos
`add_ingredient_infos(infos: list[dict], ignore_duplicates: bool = False)` - Adds multiple ingredients to the database whose data is specified in the list of ingredient information.

This is a bulk operation, which means it is equivalent to calling `add_ingredient_info()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `infos (list[dict])`: The list of ingredient information dictionaries to use to create the ingredients. The format of the dictionaries is specified under [`add_ingredient_info()`](#add-ingredient-info).
- `ignore_duplicates (bool)`: Whether this function should skip over duplicate ingredients instead of raising an error. This value is optional and is false by default.

Raises
- `DatabaseException`: If the function failed to add the ingredients.
- `DuplicateIngredientException`: If a ingredient already exists in the database with any of the specified IDs.
- `InvalidArgumentException`: If any of the provided arguments were invalid.

#### Get Multiple Ingredient Infos
`get_ingredient_infos(ingredient_ids: list[int]) -> list[Ingredient]` - Returns a list of `Ingredient` objects whose IDs match the specified ingredient IDs.

This is a bulk operation, which means it is equivalent to calling `get_ingredient_info()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `ingredient_ids (list[int])`: The IDs of the target ingredients.

Returns

A list of `Ingredient` objects whose IDs match the specified ingredient IDs.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoIngredientException`: If any of the passed IDs do not correspond to a ingredient in the database.

#### Delete Multiple Ingredient Infos
`delete_ingredient_infos(ingredient_ids: list[int])` - Deletes all of the ingredients with the specified user IDs.

This is a bulk operation, which means it is equivalent to calling `delete_ingredient_infos()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `ingredient_ids (list[int])`: The IDs of the target ingredients.

Raises
- `DatabaseException`: If the function failed to query the database.
- `NoIngredientException`: If any of the passed IDs do not correspond to a ingredient in the database.

### Friends
#### Add Relationship
`add_relationship(user1_id: str, user2_id: str)` - Adds a new relationship between the specified users.

If the two specified users already have a relationship, this function has no effect.

Args
- `user1_id (str)`: The ID of the first user in the relationship.
- `user2_id (str)`: The ID of the second user in the relationship.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If either of the specified users do not exist.

#### Has Relationship
`has_relationship(user1_id: str, user2_id: str) -> bool` - Returns true if the specified users have a relationship.

Args
- `user1_id (str)`: The ID of the first user in the relationship.
- `user2_id (str)`: The ID of the second user in the relationship.

Returns

True if the specified users have a relationship and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If either of the specified users do not exist.

#### Delete Relationship
`delete_relationship(user1_id: str, user2_id: str)` - Deletes the relationship for the specified users.

If the specified users do not have a relationship, this function has no effect.

Args
- `user1_id (str)`: The ID of the first user in the relationship.
- `user2_id (str)`: The ID of the second user in the relationship.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If either of the specified users do not exist.

#### Get Relationships for User
`get_relationships_for_user(user_id: str, offset: int = 0, limit: int = 0) -> (list[User], int)` - Returns a list of `User` objects who have relationships with the specified user and the maximum number of available results.

Args
- `user_id (str)`: The ID of the target user.
- `offset (int)`: The offset into the results to start at. This value is optional and by default is 0.
- `limit (int)`: The maximum number of results to return. This value is optional and by default is 0, which tells the database to return all available results.

Returns

A tuple containing the list of `User` objects who have relationships with the specified user and an integer describing the maximum number of available results.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified offset or limit is less than 0.

#### Add Friend Request
`add_friend_request(src: str, target: str)` - Adds a friend request from the source user to the target user.

If a friend request has already been sent from the specified source user to the specified target user, this function has no effect.

Args
- `src (str)`: The ID of the user who sent the request.
- `target (str)`: The ID of the user who will receive the request.

Returns

True if the friend request was added and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If either of the specified users do not exist.

#### Get Friend Requests for Source
`get_friend_requests_for_source(src: str, offset: int = 0, limit: int = 0) -> (list[User], int)` - Returns a list of `User` objects which are targets for friend requests from the specified source user and the maximum number of available results.

Args
- `src (str)`: The ID of the user who sent the requests.
- `offset (int)`: The offset into the results to start at. This value is optional and by default is 0.
- `limit (int)`: The maximum number of results to return. This value is optional and by default is 0, which tells the database to return all available results.

Returns

A tuple containing the list of User objects which are targets for friend requests from the specified source user and an integer describing the maximum number of available results.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified offset or limit is less than 0.

#### Get Friend Requests for Target
`get_friend_requests_for_target(target: str, offset: int = 0, limit: int = 0) -> (list[User], int)` - Returns a list of `User` objects which are sources for friend requests to the specified target user and the maximum number of available results.

Args
- `target (str)`: The ID of the user who received the requests.
- `offset (int)`: The offset into the results to start at. This value is optional and by default is 0.
- `limit (int)`: The maximum number of results to return. This value is optional and by default is 0, which tells the database to return all available results.

Returns

A tuple containing the list of `User` objects which are sources for friend requests to the specified target user and an integer describing the maximum number of available results.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified offset or limit is less than 0.

#### Delete Friend Request
`delete_friend_request(src: str, target: str) -> bool` - Deletes the friend request for the specified source and target users.

If a friend request does not exist between specified source user and the specified target user, this function has no effect.

Args
- `src (str)`: The ID of the user who sent the request.
- `target (str)`: The ID of the user who received the request.

Returns

True if the friend request was deleted and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If either of the specified users do not exist.

### User Intolerances
#### Add Intolerance
`add_intolerance(user_id: str, intolerance: UserIntolerance) -> bool` - Adds the specified intolerance to the specified user.

If the user already has the specified intolerance, this function has no effect.

Args
- `user_id (str)`: The ID of the target user.
- `intolerance (UserIntolerance)`: The target intolerance value.

Returns

True if the intolerance was added and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Has Intolerance
`has_intolerance(user_id: str, intolerance: UserIntolerance)` - Returns true if the user has the specified intolerance.

Args
- `user_id (str)`: The ID of the target user.
- `intolerance (UserIntolerance)`: The target intolerance value.

Returns

True if the user has the specified intolerance and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Delete Intolerance
`delete_intolerance(user_id: str, intolerance: UserIntolerance) -> bool` - Deletes the specified intolerance from the user's list of intolerances.

If the user does not have the specified intolerance, this function has no effect.

Args
- `user_id (str)`: The ID of the target user.
- `intolerance (UserIntolerance)`: The target intolerance value.

Returns

True if the intolerance was deleted and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Get Intolerances
`get_intolerances(user_id: str, offset: int = 0, limit: int = 0) -> (list[UserIntolerance], int)` - Returns a list of intolerances for the specified user and the maximum number of available results.

Args
- `user_id (str)`: The ID of the target user.
- `offset (int)`: The offset into the results to start at. This value is optional and by default is 0.
- `limit (int)`: The maximum number of results to return. This value is optional and by default is 0, which tells the database to return all available results.

Returns

A tuple containing the list of intolerances for the specified user, or an empty list if the user has no intolerances, and an integer describing the maximum number of available results.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified offset or limit is less than 0.

### User-Saved Recipes
#### Add Recipe
`add_recipe(user_id: str, recipe_info: dict) -> bool` - Adds the specified recipe to the user's list of saved recipes.

If the user already has the recipe saved, this function has no effect.

Args
- `user_id (str)`: The ID of the target user.
- `recipe_info (dict)`: The info for the target recipe. The format for this argument is specified in the [`add_recipe_info()`](#add-recipe-info) section. If the specified recipe does not exist in the global recipe table, this function will add it to the table.

Returns

True if the recipe was added and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If any of the provided arguments were invalid.

#### Has Recipe
`has_recipe(user_id: str, recipe_id: int) -> bool` - Returns true if the user already has the specified recipe saved in their list of recipes.

Args
- `user_id (str)`: The ID of the target user.
- `recipe_id (int)`: The ID for the target recipe.

Returns

True if the user already has the specified recipe saved in their list of recipes and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Delete Recipe
`delete_recipe(user_id: str, recipe_id: int) -> bool` - Deletes the recipe from the user's list of saved recipes.

If the user does not have the specified recipe in their list, this function has no effect.

Args
- `user_id (str)`: The ID of the target user.
- `recipe_id (int)`: The ID for the target recipe.

Returns

True if the recipe was deleted and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Get Recipes
`get_recipes(user_id: str, offset: int = 0, limit: int = 0) -> (list[Recipe], int)` - Returns a list of `Recipe` objects for which the user has in their list of saved recipes and the maximum number of available results.

Args
- `user_id (str)`: The ID of the target user.
- `offset (int)`: The offset into the results to start at. This value is optional and by default is 0.
- `limit (int)`: The maximum number of results to return. This value is optional and by default is 0, which tells the database to return all available results.

Returns

A tuple containing the list of `Recipe` objects for which the user has in their list of saved recipes, or an empty list if the user has no saved recipes, and an integer describing the maximum number of available results.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified offset or limit is less than 0.

#### Add Multiple Recipes
`add_recipes(user_ids: list[str], recipe_infos: list[dict])` - Adds each of the specified recipes to their corresponding user.

For any of the user/recipe combinations, if the user already has the specified recipe, this function has no effect for that particular combination.

This is a bulk operation, which means it is equivalent to calling `add_recipe()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `user_ids (list[str])`: The list of user IDs. This list must have the same length as `recipe_infos`.
- `recipe_infos (list[dict])`: The list of recipe information dictionaries whose format is specified [here](#add-recipe-info). This list must have the same length as `user_ids`.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If any of the specified users do not exist.
- `InvalidArgumentException`: If any of the provided arguments are invalid.

#### Delete Multiple Recipes
`delete_recipes(user_ids: list[str], recipe_ids: list[int])` - Deletes all of the specified user and recipe combinations.

For any of the user/recipe combinations, if the user does not have the specified recipe, this function has no effect for that particular combination.

This is a bulk operation, which means it is equivalent to calling `delete_recipe()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `user_ids (list[str])`: The list of user IDs. This list must have the same length as `recipe_ids`.
- `recipe_ids (list[int])`: The list of recipe IDs. This list must have the same length as `user_ids`.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If any of the specified users do not exist.

#### Get User Top Recipes
`get_user_top_recipes(user_id: str, limit: int = 5) -> list[Recipe]` - Returns a list of a random selection from the user's most recently liked recipes.

The algorithm will look at only the most recently liked recipes and will only retrieve up to the specified limit of recipes.

Args
- `user_id (str)`: The ID of the target user.
- `limit (int)`: The maximum number of recipes to return. This value is optional and is 5 by default.

Returns

A list of a random selection from the user's most recently liked recipes, or an empty list if the user has no saved recipes.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified limit is less than 0.

#### Get Friend Top Recipes
`get_friend_top_recipes(user_id: str, friend_limit: int = 5, limit_per_friend: int = 5) -> list[dict]` - Returns a list of user/recipe list pairs generated based off of the liked recipes of the specified user's friends.

The algorithm will look at only the most recently liked recipes and will only retrieve up to the specified limit of recipes per friend.

Args
- `user_id (str)`: The ID of the target user.
- `friend_limit (int)`: The maximum number of friends to look at. This value is optional and is 5 by default.
- `limit_per_friend (int)`: The maximum number of recipes to retrieve per friend. This value is optional and is 5 by default.

Returns

A list of user/recipe list pairs generated based off of the liked recipes of the specified user's friends, or an empty list if the user has no friends.

Each entry in the list is a dictionary containing the following entries:
- `user (User)`: The `User` object for the associated friend.
- `recipes (list[Recipe])`: The list of `Recipe` objects retrieved from the associated friend's list of liked recipes. This list will be empty if the associated friend has no saved recipes.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If either of the limit values are less than 0.

### User-Saved Ingredients
#### Add Ingredient
`add_ingredient(user_id: str, ingredient_info: dict) -> bool` - Adds the specified ingredient to the user's list of saved ingredients.

If the user already has the ingredient saved, this function has no effect.

Args
- `user_id (str)`: The ID of the target user.
- `ingredient_info (dict)`: The info for the target ingredient. The format for this argument is specified in the [`add_ingredient_info()`](#add-ingredient-info) section. If the specified ingredient does not exist in the global ingredient table, this function will add it to the table.

Returns

True if the ingredient was added and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If any of the provided arguments were invalid.

#### Has Ingredient
`has_ingredient(user_id: str, ingredient_id: int) -> bool` - Returns true if the user already has the specified ingredient saved in their list of ingredients.

Args
- `user_id (str)`: The ID of the target user.
- `ingredient_id (int)`: The ID for the target ingredient.

Returns

True if the user already has the specified ingredient saved in their list of ingredients and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Delete Ingredient
`delete_ingredient(user_id: str, ingredient_id: int) -> bool` - Deletes the ingredient from the user's list of saved ingredients.

If the user does not have the specified ingredient in their list, this function has no effect.

Args
- `user_id (str)`: The ID of the target user.
- `ingredient_id (int)`: The ID for the target ingredient.

Returns

True if the ingredient was deleted and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Get Ingredients
`get_ingredients(user_id: str, offset: int = 0, limit: int = 0) -> (list[Ingredient], int)` - Returns a list of `Ingredient` objects for which the user has in their list of saved ingredients and the maximum number of available results.

Args
- `user_id (str)`: The ID of the target user.
- `offset (int)`: The offset into the results to start at. This value is optional and by default is 0.
- `limit (int)`: The maximum number of results to return. This value is optional and by default is 0, which tells the database to return all available results.

Returns

A tuple containing the list of `Ingredient` objects for which the user has in their list of saved ingredients, or an empty list if the user has no saved ingredients, and an integer describing the maximum number of available results.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified offset or limit is less than 0.

#### Add Multiple Ingredients
`add_ingredients(user_ids: list[str], ingredient_infos: list[dict])` - Adds each of the specified ingredients to their corresponding user.

For any of the user/ingredient combinations, if the user already has the specified ingredient, this function has no effect for that particular combination.

This is a bulk operation, which means it is equivalent to calling `add_ingredient()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `user_ids (list[str])`: The list of user IDs. This list must have the same length as `ingredient_infos`.
- `ingredient_infos (list[dict])`: The list of ingredient information dictionaries whose format is specified [here](#add-ingredient-info). This list must have the same length as `user_ids`.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If any of the specified users do not exist.
- `InvalidArgumentException`: If any of the provided arguments are invalid.

#### Delete Multiple Ingredients
`delete_ingredients(user_ids: list[str], ingredient_ids: list[int])` - Deletes all of the specified user and ingredient combinations.

For any of the user/ingredient combinations, if the user does not have the specified ingredient, this function has no effect for that particular combination.

This is a bulk operation, which means it is equivalent to calling `delete_ingredient()` repeatedly, but this function is faster because it batches all of the operations into a single database call.

Args
- `user_ids (list[str])`: The list of user IDs. This list must have the same length as `ingredient_ids`.
- `ingredient_ids (list[int])`: The list of ingredient IDs. This list must have the same length as `user_ids`.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If any of the specified users do not exist.

#### Get User Top Ingredients
`get_user_top_ingredients(user_id: str, limit: int = 5) -> list[Ingredient]` - Returns a list of a random selection from the user's most recently liked ingredients.

The algorithm will look at only the most recently liked ingredients and will only retrieve up to the specified limit of ingredients.

Args
- `user_id (str)`: The ID of the target user.
- `limit (int)`: The maximum number of ingredients to return. This value is optional and is 5 by default.

Returns

A list of a random selection from the user's most recently liked ingredients, or an empty list if the user has no saved ingredients.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified limit is less than 0.

#### Get Friend Top Ingredients
`get_friend_top_ingredients(user_id: str, friend_limit: int = 5, limit_per_friend: int = 5) -> list[dict]` - Returns a list of user/ingredient list pairs generated based off of the liked ingredients of the specified user's friends.

The algorithm will look at only the most recently liked ingredients and will only retrieve up to the specified limit of ingredients per friend.

Args
- `user_id (str)`: The ID of the target user.
- `friend_limit (int)`: The maximum number of friends to look at. This value is optional and is 5 by default.
- `limit_per_friend (int)`: The maximum number of ingredients to retrieve per friend. This value is optional and is 5 by default.

Returns

A list of user/ingredient list pairs generated based off of the liked ingredients of the specified user's friends, or an empty list if the user has no friends.

Each entry in the list is a dictionary containing the following entries:
- `user (User)`: The `User` object for the associated friend.
- `ingredients (list[Ingredient])`: The list of `Ingredient` objects retrieved from the associated friend's list of liked ingredients. This list will be empty if the associated friend has no saved ingredients.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If either of the limit values are less than 0.

### User Account Management
#### Set Username
`set_username(user_id: str, username: str)` - Sets the username for the specified user.

Args
- `user_id (str)`: The ID of the target user.
- `username (str)`: The username for the target user. This value must be unique across all users and must conform to the syntax rules specified in the [`users`](#users) table.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `DuplicateUserException`: If the specified username is already taken.
- `InvalidArgumentException`: If the specified username is syntactically invalid.

#### Set Email
`set_email(user_id: str, email: str)` - Sets the email for the specified user.

Args
- `user_id (str)`: The ID of the target user.
- `email (str)`: The email for the target user. This value must be unique across all users and must conform to regular email syntax rules.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `DuplicateUserException`: If the specified email is already taken.
- `InvalidArgumentException`: If the specified email is syntactically invalid.

#### Set Password
`set_password(user_id: str, password: str, encrypted: bool = False)` - Sets the password for the specified user.

This function is only applicable for users whose authentication method is `DEFAULT`.

Args
- `user_id (str)`: The ID of the target user.
- `password (str)`: The password for the target user.
- `encrypted (bool)`: Whether the passed password is already encrypted. This value is false by default.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified user does not have an account type which supports a password.
- `EncryptionException`: If there was a problem handling the encryption for the password.

#### Validate Password
`validate_password(user_id: str, password: str) -> bool` - Returns true if the provided unencrypted password matches the password stored in the database for the specified user.

If the stored password needs to be rehashed, this function will rehash it and update it in the database.

Args
- `user_id (str)`: The ID of the target user.
- `password (str)`: The password for the target user.

Returns

True if the the provided unencrypted password matches the password stored in the database for the specified user and false otherwise.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.
- `InvalidArgumentException`: If the specified user does not have an account type which supports a password.
- `EncryptionException`: If there was a problem handling the encryption for the password.

#### Set Profile Image
`set_profile_image(user_id: str, profile_image: str)` - Sets the profile image URL for the specified user.

Args
- `user_id (str)`: The ID of the target user.
- `profile_image (str)`: The URL for the target user's profile image.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Set User Status
`set_user_status(user_id: str, status: UserStatus)` - Sets the status for the specified user.

Args
- `user_id (str)`: The ID of the target user.
- `status (UserStatus)`: The status of the target user.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Set Name
`set_name(user_id: str, given_name: str, family_name: str)` - Sets the name for the specified user.

If you only want to set the given name and not the family name (or vice versa), set the one you don't want to change to `None` or use `set_given_name()` or `set_family_name()`.

Args
- `user_id (str)`: The ID of the target user.
- `given_name (str)`: The given name of the target user.
- `family_name (str)`: The family name of the target user.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Set Given Name
`set_given_name(user_id: str, given_name: str)` - Sets the given name for the specified user.

Args
- `user_id (str)`: The ID of the target user.
- `given_name (str)`: The given name of the target user.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Set Family Name
`set_family_name(user_id: str, family_name: str)` - Sets the family name for the specified user.

Args
- `user_id (str)`: The ID of the target user.
- `family_name (str)`: The family name of the target user.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.

#### Set Profile Visibility
`set_profile_visibility(user_id: str, profile_visibility: int)` - Sets the profile visibility for the specified user.

Args
- `user_id (str)`: The ID of the target user.
- `profile_visibility (int)`: The profile visibility for the target user.

Raises
- `DatabaseException`: If there was a problem querying the database.
- `NoUserException`: If the specified user does not exist.