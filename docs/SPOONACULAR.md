# Spoonacular API
The following document details the Spoonacular third-party API calls and related types.

## Table of Contents
- [Spoonacular API](#spoonacular-api)
  - [Table of Contents](#table-of-contents)
  - [Types](#types)
  - [Functions](#functions)

## Types
`SpoonacularApiException` - Raised if there is a problem making a Spoonacular API call.

<br/>

`Intolerance` - The available intolerances that can be fed to the Spoonacular API calls, such as for `search_recipes()`.

| Element Name |   Value   |
| :----------: | :-------: |
|   `Dairy`    |   Dairy   |
|    `Egg`     |    Egg    |
|   `Gluten`   |  Gluten   |
|   `Grain`    |   Grain   |
|   `Peanut`   |  Peanut   |
|  `Seafood`   |  Seafood  |
|   `Sesame`   |  Sesame   |
| `Shellfish`  | Shellfish |
|    `Soy`     |    Soy    |
|  `Sulfite`   |  Sulfite  |
|  `TreeNut`   | Tree Nut  |
|   `Wheat`    |   Wheat   |

<br/>

`Cuisine` - The available cuisines that can be fed to the Spoonacular API calls, such as for `search_recipes()`.

|   Element Name    |      Value       |
| :---------------: | :--------------: |
|     `African`     |     African      |
|    `American`     |     American     |
|     `British`     |     British      |
|      `Cajun`      |      Cajun       |
|    `Caribbean`    |    Caribbean     |
|     `Chinese`     |     Chinese      |
| `EasternEuropean` | Eastern European |
|    `European`     |     European     |
|     `French`      |      French      |
|     `German`      |      German      |
|      `Greek`      |      Greek       |
|     `Indian`      |      Indian      |
|      `Irish`      |      Irish       |
|     `Italian`     |     Italian      |
|    `Japanese`     |     Japanese     |
|     `Jewish`      |      Jewish      |
|     `Korean`      |      Korean      |
|  `LatinAmerican`  |  Latin American  |
|  `Mediterranean`  |  Mediterranean   |
|     `Mexican`     |     Mexican      |
|  `MiddleEastern`  |  Middle Eastern  |
|     `Nordic`      |      Nordic      |
|    `Southern`     |     Southern     |
|     `Spanish`     |     Spanish      |
|      `Thai`       |       Thai       |
|   `Vietnamese`    |    Vietnamese    |

<br/>

`Diet` - The available diets that can be fed to the Spoonacular API calls, such as for `search_recipes()`.

|   Element Name    |      Value       |
| :---------------: | :--------------: |
|   `GlutenFree`    |   Gluten Free    |
|    `Ketogenic`    |    Ketogenic     |
|   `Vegetarian`    |    Vegetarian    |
| `LactoVegetarian` | Lacto-Vegetarian |
|  `OvoVegetarian`  |  Ovo-Vegetarian  |
|      `Vegan`      |      Vegan       |
|   `Pescetarian`   |   Pescetarian    |
|      `Paleo`      |      Paleo       |
|     `Primal`      |      Primal      |
|    `LowFodmap`    |    Low FODMAP    |
|     `Whole30`     |     Whole30      |

<br/>

`SortCriteria` - The available criteria used to sort the results returned by `search_recipes()`.

|      Element Name       |  Spoonacular API Value  |
| :---------------------: | :---------------------: |
|      `Popularity`       |       popularity        |
|      `Healthiness`      |       healthiness       |
|         `Price`         |          price          |
|         `Time`          |          time           |
|        `Random`         |         random          |
|  `MaxUsedIngredients`   |  max-used-ingredients   |
| `MinMissingIngredients` | min-missing-ingredients |
|       `Calories`        |        calories         |
|     `Carbohydrates`     |      carbohydrates      |
|       `TotalFat`        |        total-fat        |
|        `Protein`        |         protein         |
|         `Sugar`         |          sugar          |
|        `Sodium`         |         sodium          |

<br/>

`Recipe` - Represents a recipe.

<br/>

`Ingredient` - Represents an ingredient.

<br/>

## Functions
`get_api_key() -> str` - Returns the Spoonacular API key.

<br/>

`search_recipes(ingredients: list[str], intolerances: list[Intolerance] = None, cuisines: list[Cuisine], diets: list[Diet], max_prep_time: int, sort_by: SortCriteria, offset: int, limit: int) -> list` - Searches for recipes using the specified criteria and returns a list of JSON-encoded recipes.

<br/>

`get_recipe(id: int) -> Recipe` - Returns a `Recipe` object associated with the specified ID.

<br/>

`get_similar_recipes(id: int) -> list` - Returns a list of (JSON-encoded) recipes similar to the recipe with the specified ID.

<br/>

`search_ingredients(query: str, intolerances: list[Intolerance], sort_by: SortCriteria, offset: int, limit: int) -> list` - Searches for ingredients using the specified criteria and returns a list of JSON-encoded recipes.

<br/>

`get_ingredient(id: int) -> Ingredient` - Returns an `Ingredient` object associated with the specified ID.