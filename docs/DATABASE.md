# Database API
The following document details the database API calls and types.

## Table of Contents
- [Database API](#database-api)
  - [Table of Contents](#table-of-contents)
  - [Types](#types)
  - [Functions](#functions)
    - [Querying the Database](#querying-the-database)
    - [Adding Information to the Database](#adding-information-to-the-database)
    - [Removing Information from the Database](#removing-information-from-the-database)

## Types
`DatabaseException` - Raised when there is a general problem during a database access.

<br/>

`NoUserException` - Raised when the specified user does not exist in the database.

<br/>

`NoRecipeException` - Raised when the specified recipe does not exist in the database.

<br/>

`NoIngredientException` - Raised when the specified ingredient does not exist in the database.

<br/>

`DuplicateUserException` - Raised when the specified user already exists in the database.

<br/>

`DuplicateRecipeException` - Raised when the specified recipe already exists in the database.

<br/>

`DuplicateIngredientException` - Raised when the specified ingredient already exists in the database.

<br/>

`InvalidIntoleranceException` - Raised when the specified intolerance is invalid.

<br/>

`Database` - The object which contains all of the API calls related to the database.

<br/>

## Functions
### Querying the Database
`get_user(id: str) -> User` - Returns the `User` object associated with the provided user ID.

<br/>

`user_exists(id: str) -> bool` - Returns true if the user with the specified ID exists.

<br/>

`get_recipe(id: int) -> Recipe` - Returns the `Recipe` object associated with the provided ID.

<br/>

`get_ingredient(id: int) -> Ingredient` - Returns the `Ingredient` object associated with the provided ID.

<br/>

`get_saved_recipes(user_id: str) -> list[Recipe]` - Returns the list of saved recipes for the user with the specified ID.

<br/>

`get_saved_ingredients(user_id: str) -> list[Ingredient]` - Returns the list of saved ingredients for the user with the specified ID.

<br/>

`get_intolerances(user_id: str) -> list[str]` - Returns the list of intolerances for the user with the specified ID.

<br/>

`has_relationship(user1: str, user2: str) -> bool:` - Returns true if a relationship between the specified users exists.

- A relationship does not consider the position of the users to be significant when determining if a relationship exists. This means that for users A and B, calling `has_relationship(A, B)` is the same as calling `has_relationship(B, A)`.

<br/>

`get_relationships_for_user(user: str) -> list[User]` - Returns a list of user objects which have relationships with the specified user.

<br/>

`get_recommended_recipes_from_user(user: str, limit: int) -> list[Recipe]` - Returns a list of recipe objects based on the specified user's saved recipes.

- The algorithm will look at only the most recently liked recipes and will only retrieve up to the specified limit of recipes.

<br/>

`get_recommended_recipes_from_relationships(user: str, limit_friends: int, limit_per_relationship: int) -> dict` - Returns a JSON object containing lists of recipes generated based off of the liked recipes of the specified user's friends.

- The algorithm will look at only the most recently liked recipes and will only retrieve up to the specified limit of recipes per friend.

- The value returned will be a JSON object containing lists of recommended recipes, whose format is the following:
```json
{
    "id1": {
        "userdata": <user_obj>,
        "recipes": [<recipe_obj>]
    },
    "id2": {
        "userdata": <user_obj>,
        "recipes": [<recipe_obj>]
    },
    ...
}
```

- The returned object is a dictionary of user IDs to values containing two fields.

- `userdata` maps to the JSON representation of the associated user object.
- `recipes` maps to a list containing JSON representations of the selected recipe objects.

<br/>

`get_recommended_ingredients_from_user(user: str, limit: int) -> list[Ingredient]` - Returns a list of ingredient objects based on the specified user's saved ingredients.

- The algorithm will look at only the most recently liked ingredients and will only retrieve up to the specified limit of ingredients.

<br/>

`get_recommended_ingredients_from_relationships(user: str, limit_friends: int, limit_per_relationship: int) -> dict` - Returns a JSON object containing lists of ingredients generated based off of the liked ingredients of the specified user's friends.

- The algorithm will look at only the most recently liked ingredients and will only retrieve up to the specified limit of ingredients per friend.

- The value returned will be a JSON object containing lists of recommended ingredients, whose format is the following:
```json
{
    "id1": {
        "userdata": <user_obj>,
        "ingredients": [<ingredient_obj>]
    },
    "id2": {
        "userdata": <user_obj>,
        "ingredients": [<ingredient_obj>]
    },
    ...
}
```

- The returned object is a dictionary of user IDs to values containing two fields.

- `userdata` maps to the JSON representation of the associated user object.
- `ingredients` maps to a list containing JSON representations of the selected ingredient objects.

<br/>

### Adding Information to the Database
`add_user(id: str, email: str, name: str, profile_image: str) -> User` - Creates a new user with the specified information and adds it to the database, then returns the created user.

<br/>

`add_recipe(id: int, name: str, image: str) -> Recipe` - Creates a new recipe with the specified information and adds it to the database, then returns the created recipe.

<br/>

`add_ingredient(id: int, name: str, image: str) -> Ingredient` - Creates a new ingredient with the specified information and adds it to the database, then returns the created ingredient.

<br/>

`add_saved_recipe(user_id: str, recipe_id: int)` - Adds the recipe with the specified ID to the specified user's list of saved recipes.

<br/>

`add_saved_ingredient(user_id: str, ingredient_id: int)` - Adds the ingredient with the specified ID to the specified user's list of saved ingredients.

<br/>

`add_intolerance(user_id: str, intolerance: str)` - Adds the tolerance with the specified name to the specified user's list of saved intolerances.

<br/>

`add_relationship(user1: str, user2: str) -> bool` - Adds a two-way relationship between the specified users.

- If the relationship already exists, this function does nothing.

- A relationship does not consider the position of the users to be significant when determining if a relationship exists. This means that for users A and B, calling `add_relationship(A, B)` is the same as calling `add_relationship(B, A)`.

<br/>

### Removing Information from the Database
`delete_user(id: str)` - Deletes the user with the specified ID, including all associated rows in any linked tables (cascade delete).

<br/>

`delete_recipe(id: int)` - Deletes the recipe with the specified ID, including all associated rows in any linked tables (cascade delete).

- It's not recommended to call this function unless no users have this recipe saved, otherwise it may cause problems for those that still do!

<br/>

`delete_ingredient(id: int)` - Deletes the ingredient with the specified ID, including all associated rows in any linked tables (cascade delete).

- It's not recommended to call this function unless no users have this ingredient saved, otherwise it may cause problems for those that still do!

<br/>

`delete_saved_recipe(user_id: str, recipe_id: int)` - Deletes the recipe saved by the specified user.

- If the user does not have the recipe saved, this function has no effect.

<br/>

`delete_saved_ingredient(user_id: str, ingredient_id: int)` - Deletes the ingredient saved by the specified user.

- If the user does not have the ingredient saved, this function has no effect.

<br/>

`delete_intolerance(user_id: str, intolerance: str)` - Deletes the intolerance associated with the specified user.

- If the user does not have the associated intolerance, this function has no effect.

<br/>

`delete_relationship(user1: str, user2: str) -> bool` - Deletes the relationship between the specified users.

- If the relationship does not exist, this function does nothing.