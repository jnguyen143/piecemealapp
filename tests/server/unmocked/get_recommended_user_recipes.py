"""
This file tests the functionality of `database.Database.get_recommended_user_recipes()`.

This file injects a random number of randomly generated users, recipes, and saved recipes, then tests to ensure that `get_recommended_user_recipes()` returns the expected result given the ID of a user from the list of dummy users.
"""

import unittest
from random import randrange, seed, randint


def init_app_module_dir():
    import sys
    import pathlib

    path = str(
        pathlib.Path(__file__).parent.parent.parent.parent.joinpath("src").resolve()
    )
    sys.path.append(path)


INPUT = "input"
EXPECTED_OUTPUT = "expected"


def generate_prefixed_string(prefix):
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


def generate_recipe():
    id = randint(0, 100000)
    name = generate_prefixed_string("saved_recipe_")
    image = generate_prefixed_string("image_")
    return {"id": id, "name": name, "image": image}


def generate_recipes(seedval):
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 100)):
        recipe = generate_recipe()
        if recipe["id"] in result:
            continue
        result[recipe["id"]] = recipe
    return result


def generate_user():
    email = generate_prefixed_string("email_")
    id = generate_prefixed_string("id_")
    return {"email": email, "id": id}


def generate_users(seedval):
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 100)):
        user = generate_user()
        if user["id"] in result:
            continue
        result[user["id"]] = user
    return result


def generate_saved_recipe(users, recipes):
    user_ids = list(users.keys())
    recipe_ids = list(recipes.keys())
    user_id_idx = randrange(0, len(users))
    recipe_id_idx = randrange(0, len(recipes))
    return {"user_id": user_ids[user_id_idx], "recipe_id": recipe_ids[recipe_id_idx]}


def generate_saved_recipes(seedval, users, recipes):
    seed(seedval)
    result = []
    for _ in range(0, randint(1, len(recipes))):
        result.append(generate_saved_recipe(users, recipes))
    return result


def generate_user_id(seedval, users):
    seed(seedval)
    user_ids = list(users.keys())
    target = randrange(0, len(user_ids))
    return user_ids[target]


def generate_limit(seedval):
    seed(seedval)
    return randint(1, 10)


def get_expected_output(user_id, saved_recipes, recipes, limit):
    actual_recipes = []
    for saved_recipe in saved_recipes:
        if saved_recipe["user_id"] == user_id:
            actual_recipes.append(recipes[saved_recipe["recipe_id"]])

    return actual_recipes[-limit:]


def recipes_match(mock_recipe, db_recipe):
    return (
        db_recipe.id == mock_recipe["id"]
        and db_recipe.name == mock_recipe["name"]
        and db_recipe.image == mock_recipe["image"]
    )


def contains_recipe(expected_output, target):
    for recipe in expected_output:
        if recipes_match(recipe, target):
            return True
    return False


def validate_input(actual_output, expected_output):
    for output in actual_output:
        if not contains_recipe(expected_output, output):
            return False
    return True


class GetRecommendedUserRecipesTestCase(unittest.TestCase):
    def setUp(self):
        self.test_success_params = []
        for _ in range(0, 10):
            seedval = randint(0, 100)
            recipes = generate_recipes(seedval)
            users = generate_users(seedval)
            saved_recipes = generate_saved_recipes(seedval, users, recipes)
            user_id = generate_user_id(seedval, users)
            limit = generate_limit(seedval)
            self.test_success_params.append(
                {
                    INPUT: {
                        "seedval": seedval,
                        "recipes": recipes,
                        "users": users,
                        "saved_recipes": saved_recipes,
                        "user_id": user_id,
                        "limit": limit,
                    },
                    EXPECTED_OUTPUT: get_expected_output(
                        user_id, saved_recipes, recipes, limit
                    ),
                }
            )

    def runTest(self):
        init_app_module_dir()
        # If the below comment is not present, pylance will generate an import warning. We know the import is valid because the above function call injects the required module directory.
        import app  # pyright: reportMissingImports=false

        app.init_app()
        for test in self.test_success_params:
            for recipe in test[INPUT]["recipes"].values():
                app.db.add_recipe(recipe["id"], recipe["name"], recipe["image"])
            for user in test[INPUT]["users"].values():
                app.db.add_google_user(user["id"], user["email"])
            for saved_recipe in test[INPUT]["saved_recipes"]:
                app.db.add_saved_recipe(
                    saved_recipe["user_id"], saved_recipe["recipe_id"]
                )
            validation = False
            try:
                validation = validate_input(
                    app.db.get_recommended_recipes_from_user(
                        test[INPUT]["user_id"], test[INPUT]["limit"]
                    ),
                    test[EXPECTED_OUTPUT],
                )
            except:
                pass
            finally:
                for user in test[INPUT]["users"].keys():
                    app.db.delete_user(user)
                for recipe in test[INPUT]["recipes"].keys():
                    app.db.delete_recipe(recipe)

            self.assertTrue(
                validation,
                f"Assertion failed for input with seed {test[INPUT]['seedval']}",
            )


if __name__ == "__main__":
    unittest.main()
