"""
This file tests the functionality of `database.Database.get_recommended_user_recipes()`.

This file injects a random number of randomly generated users, recipes, and saved recipes,
then tests to ensure that `get_recommended_user_recipes()` returns the expected result given
the ID of a user from the list of dummy users.
"""

import unittest
from random import randrange, seed, randint
from .... import app


INPUT = "input"
EXPECTED_OUTPUT = "expected"


def generate_prefixed_string(prefix):
    """
    Generates a random string with the specified prefix.
    """
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


def generate_recipe():
    """
    Generates a random recipe.
    """
    recipe_id = randint(0, 100000)
    name = generate_prefixed_string("saved_recipe_")
    image = generate_prefixed_string("image_")
    summary = generate_prefixed_string("summary_")
    full_summary = generate_prefixed_string("full_summary_")
    return {
        "id": recipe_id,
        "name": name,
        "image": image,
        "summary": summary,
        "full_summary": full_summary,
    }


def generate_recipes(seedval):
    """
    Generates a random list of recipes.
    """
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 10)):
        recipe = generate_recipe()
        if recipe["id"] in result:
            continue
        result[recipe["id"]] = recipe
    return result


def generate_user():
    """
    Generates a random user.
    """
    email = generate_prefixed_string("email_") + "@testcase.com"
    user_id = generate_prefixed_string("id_")
    return {"email": email, "id": user_id, "authentication": 1}


def emails_match(dct: dict, user):
    """
    Returns true if the user emails match.
    """
    for val in dct.values():
        if val["email"] == user["email"]:
            return True
    return False


def generate_users(seedval):
    """
    Generates a random list of users.
    """
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 10)):
        user = generate_user()
        if user["id"] in result or emails_match(result, user):
            continue
        result[user["id"]] = user
    return result


def generate_saved_recipe(users, recipes):
    """
    Generates a random saved recipe.
    """
    user_ids = list(users.keys())
    recipe_ids = list(recipes.keys())
    user_id_idx = randrange(0, len(users))
    recipe_id_idx = randrange(0, len(recipes))
    return {"user_id": user_ids[user_id_idx], "recipe_id": recipe_ids[recipe_id_idx]}


def generate_saved_recipes(seedval, users, recipes):
    """
    Generates a random list of saved recipes.
    """
    seed(seedval)
    result = []
    if len(recipes) == 0:
        return []
    for _ in range(0, randint(1, len(recipes))):
        result.append(generate_saved_recipe(users, recipes))
    return result


def generate_user_id(seedval, users):
    """
    Generates a random user ID.
    """
    seed(seedval)
    user_ids = list(users.keys())
    target = randrange(0, len(user_ids))
    return user_ids[target]


def generate_limit(seedval):
    """
    Generates a random limit.
    """
    seed(seedval)
    return randint(1, 10)


def get_expected_output(user_id, saved_recipes, recipes, limit):
    """
    Returns the expected output for this test.
    """
    actual_recipes = []
    for saved_recipe in saved_recipes:
        if saved_recipe["user_id"] == user_id:
            actual_recipes.append(recipes[saved_recipe["recipe_id"]])

    return actual_recipes[-limit:]


def recipes_match(mock_recipe, db_recipe):
    """
    Returns true if the two recipes match.
    """
    return (
        db_recipe.id == mock_recipe["id"]
        and db_recipe.name == mock_recipe["name"]
        and db_recipe.image == mock_recipe["image"]
        and db_recipe.summary == mock_recipe["summary"]
        and db_recipe.full_summary == mock_recipe["full_summary"]
    )


def contains_recipe(expected_output, target):
    """
    Returns true if the expected output contains the target.
    """
    for recipe in expected_output:
        if recipes_match(recipe, target):
            return True
    return False


def validate_input(actual_output, expected_output):
    """
    Returns true if the actual output matches the expected output.
    """
    for output in actual_output:
        if not contains_recipe(expected_output, output):
            return False
    return True


class GetRecommendedUserRecipesTestCase(unittest.TestCase):
    """
    Holds the actual test data.
    """

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def setUp(self):
        """
        Sets up the test.
        """
        self.test_success_params = []
        for _ in range(0, 5):
            seedval = randint(0, 100)
            recipes = generate_recipes(seedval)
            users = generate_users(seedval)
            saved_recipes = generate_saved_recipes(seedval, users, recipes)
            if len(users) == 0:
                continue
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

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def runTest(self):
        """
        Runs the test.
        """
        print("\033[0;33m===== TEST: GetRecommendedUserRecipes =====\033[0m")
        app.init_app()
        total_test_amount = len(self.test_success_params)
        for current_test_index, _ in enumerate(self.test_success_params):
            test = self.test_success_params[current_test_index]
            print(
                f"""\033[0;33m----- Executing test {current_test_index + 1} \
of {total_test_amount} -----\033[0m"""
            )
            print("Injecting test data...")

            validation = False
            try:
                app.DATABASE.add_users(test[INPUT]["users"].values())
                app.DATABASE.add_recipe_infos(test[INPUT]["recipes"].values())

                recipe_infos = []
                user_ids = []
                for recipe in test[INPUT]["saved_recipes"]:
                    recipe_infos.append(test[INPUT]["recipes"][recipe["recipe_id"]])
                    user_ids.append(recipe["user_id"])

                app.DATABASE.add_recipes(user_ids, recipe_infos)

                print("Validating...")
                validation = validate_input(
                    app.DATABASE.get_user_top_recipes(
                        test[INPUT]["user_id"], test[INPUT]["limit"]
                    ),
                    test[EXPECTED_OUTPUT],
                )
            # pylint: disable=broad-except
            # We want to catch all exceptions just in case
            except Exception:
                pass
            finally:
                print("Deleting test data...")
                app.DATABASE.delete_users(list(test[INPUT]["users"]))
                app.DATABASE.delete_recipe_infos(list(test[INPUT]["recipes"]))

            if validation:
                print("Result: \033[92mPASS\033[0m")
            else:
                print("Result: \033[91mFAIL\033[0m")

            self.assertTrue(
                validation,
                f"Assertion failed for input with seed {test[INPUT]['seedval']}",
            )


if __name__ == "__main__":
    unittest.main()
