# pylint: disable=(C0114)
# pylint: disable=(E0401)
# disabled the above errors and error E0116
# because
import unittest
import sys
import pathlib
from random import randrange, seed, randint


# pylint: disable=(W0105)
# disabled the above, error
# was the comment below
# was pointless, for
# stating pupose of file
"""
This file tests the functionality of `database.Database.get_recommended_user_recipes()`.

This file injects a random number of randomly generated users, recipes, and saved recipes,
then tests to ensure that `get_recommended_user_recipes()` returns the expected result given
the ID of a user from the list of dummy users.
"""

# pylint: disable=(C0116)
def init_app_module_dir():

    path = str(
        pathlib.Path(__file__).parent.parent.parent.parent.joinpath("src").resolve()
    )
    sys.path.append(path)


INPUT = "input"
EXPECTED_OUTPUT = "expected"

# pylint: disable=(C0116)
def generate_prefixed_string(prefix):
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


# pylint: disable=(C0116)
def generate_recipe():
    # pylint: disable=(C0103)
    # fixing snake case name error
    # pylint: disable=(W0622)
    # disabling redefined built
    # error, as this does not
    # affect code functionality
    id = randint(0, 100000)
    name = generate_prefixed_string("saved_recipe_")
    image = generate_prefixed_string("image_")
    summary = generate_prefixed_string("summary_")
    full_summary = generate_prefixed_string("full_summary_")
    return {
        "id": id,
        "name": name,
        "image": image,
        "summary": summary,
        "full_summary": full_summary,
    }


# pylint: disable=(C0116)
def generate_recipes(seedval):
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 10)):
        recipe = generate_recipe()
        if recipe["id"] in result:
            continue
        result[recipe["id"]] = recipe
    return result


# pylint: disable=(C0116)
def generate_user():
    email = generate_prefixed_string("email_")
    # pylint: disable=(C0103)
    # disabled snake case error
    # pylint: disable=(W0622)
    # disabling redefined
    # built in error
    id = generate_prefixed_string("id_")
    return {"email": email, "id": id}


# pylint: disable=(C0116)
def generate_users(seedval):
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 10)):
        user = generate_user()
        if user["id"] in result:
            continue
        result[user["id"]] = user
    return result


# pylint: disable=(C0116)
def generate_saved_recipe(users, recipes):
    user_ids = list(users.keys())
    recipe_ids = list(recipes.keys())
    user_id_idx = randrange(0, len(users))
    recipe_id_idx = randrange(0, len(recipes))
    return {"user_id": user_ids[user_id_idx], "recipe_id": recipe_ids[recipe_id_idx]}


# pylint: disable=(C0116)
def generate_saved_recipes(seedval, users, recipes):
    seed(seedval)
    result = []
    for _ in range(0, randint(1, len(recipes))):
        result.append(generate_saved_recipe(users, recipes))
    return result


# pylint: disable=(C0116)
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
        and db_recipe.summary == mock_recipe["summary"]
        and db_recipe.full_summary == mock_recipe["full_summary"]
    )


# pylint: disable=(C0116)
def contains_recipe(expected_output, target):
    for recipe in expected_output:
        if recipes_match(recipe, target):
            return True
    return False


# pylint: disable=(C0115)
def validate_input(actual_output, expected_output):
    for output in actual_output:
        if not contains_recipe(expected_output, output):
            return False
    return True


class GetRecommendedUserRecipesTestCase(unittest.TestCase):
    # pylint: disable=(C0116)
    def setUp(self):
        self.test_success_params = []
        for _ in range(0, 5):
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

    # pylint: disable=(C0116)
    # pylint: disable=(C0103)
    # disable snake case
    # error menu and function
    # error as it does not
    # affect any code functionality

    def runTest(self):
        print("\033[0;33m===== TEST: GetRecommendedUserRecipes =====\033[0m")
        init_app_module_dir()
        import app

        # If the below comment is not present,
        # pylance will generate an import warning.
        # We know the import is valid because the
        # above function call injects the required module directory.
        # pyright: reportMissingImports=false

        app.init_app()
        total_test_amount = len(self.test_success_params)
        # pylint: disable=(C0200)
        # disabled consider using
        # error
        for current_test_index in range(0, len(self.test_success_params)):
            test = self.test_success_params[current_test_index]
            # pylint: disable=(C0301)
            # the error above is regarding
            # the print statement being too
            # long, had to disable this
            # feature
            print(
                f"\033[0;33m----- Executing test {current_test_index + 1} of {total_test_amount} -----\033[0m"
            )
            print("Injecting test data...")
            app.db.add_recipes(test[INPUT]["recipes"].values())
            app.db.add_google_users(test[INPUT]["users"].values())
            app.db.add_saved_recipes(test[INPUT]["saved_recipes"])

            validation = False
            try:
                print("Validating...")
                validation = validate_input(
                    app.db.get_recommended_recipes_from_user(
                        test[INPUT]["user_id"], test[INPUT]["limit"]
                    ),
                    test[EXPECTED_OUTPUT],
                )
            # pylint: disable=(W0702)
            # disabled except error
            except:
                pass
            finally:
                print("Deleting test data...")
                for user in test[INPUT]["users"].keys():
                    app.db.delete_user(user)
                for recipe in test[INPUT]["recipes"].keys():
                    app.db.delete_recipe(recipe)

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
