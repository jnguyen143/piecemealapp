# pylint: disable=(C0114)
# pylint: disable=(E0401)
# disabled the above errors and error
# C0116 due to it not having
# an effect on code functionality
import unittest
from random import randrange, seed, randint
import sys
import pathlib


# pylint: disable=(W0105)
# disabled error for string
# comment below
# being declared as useless
"""
This file tests the functionality of `database.Database.get_recommended_user_ingredients()`.

This file injects a random number of randomly generated users, ingredients,
and saved ingredients, then tests to ensure that `get_recommended_user_ingredients()`
returns the expected result given the ID of a user from the list of dummy users.
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


def generate_ingredient():
    # pylint: disable=(C0103)
    # disbled snake case error
    # pylint: disable=(W0622)
    # disabled redefined built in
    # error
    id = randint(0, 100000)
    name = generate_prefixed_string("saved_ingredient_")
    image = generate_prefixed_string("image_")
    return {"id": id, "name": name, "image": image}


def generate_ingredients(seedval):
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 10)):
        ingredient = generate_ingredient()
        if ingredient["id"] in result:
            continue
        result[ingredient["id"]] = ingredient
    return result


def generate_user():
    email = generate_prefixed_string("email_")
    # pylint: disable=(C0103)
    # disabled snake case error
    # pylint: disable=(W0622)
    # disabled redefined built in
    # error, as this does not
    # affect code
    # functionality
    id = generate_prefixed_string("id_")
    return {"email": email, "id": id}


def generate_users(seedval):
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 10)):
        user = generate_user()
        if user["id"] in result:
            continue
        result[user["id"]] = user
    return result


def generate_saved_ingredient(users, ingredients):
    user_ids = list(users.keys())
    ingredient_ids = list(ingredients.keys())
    user_id_idx = randrange(0, len(users))
    ingredient_id_idx = randrange(0, len(ingredients))
    return {
        "user_id": user_ids[user_id_idx],
        "ingredient_id": ingredient_ids[ingredient_id_idx],
    }


def generate_saved_ingredients(seedval, users, ingredients):
    seed(seedval)
    result = []
    for _ in range(0, randint(1, len(ingredients))):
        result.append(generate_saved_ingredient(users, ingredients))
    return result


def generate_user_id(seedval, users):
    seed(seedval)
    user_ids = list(users.keys())
    target = randrange(0, len(user_ids))
    return user_ids[target]


def generate_limit(seedval):
    seed(seedval)
    return randint(1, 10)


def get_expected_output(user_id, saved_ingredients, ingredients, limit):
    actual_ingredients = []
    for saved_ingredient in saved_ingredients:
        if saved_ingredient["user_id"] == user_id:
            actual_ingredients.append(ingredients[saved_ingredient["ingredient_id"]])

    return actual_ingredients[-limit:]


def ingredients_match(mock_ingredient, db_ingredient):
    return (
        db_ingredient.id == mock_ingredient["id"]
        and db_ingredient.name == mock_ingredient["name"]
        and db_ingredient.image == mock_ingredient["image"]
    )


def contains_ingredient(expected_output, target):
    for ingredient in expected_output:
        if ingredients_match(ingredient, target):
            return True
    return False


def validate_input(actual_output, expected_output):
    for output in actual_output:
        if not contains_ingredient(expected_output, output):
            return False
    return True


# pylint: disable=(C0115)
class GetRecommendedUserIngredientsTestCase(unittest.TestCase):
    def setUp(self):
        self.test_success_params = []
        for _ in range(0, 5):
            seedval = randint(0, 100)
            ingredients = generate_ingredients(seedval)
            users = generate_users(seedval)
            saved_ingredients = generate_saved_ingredients(seedval, users, ingredients)
            user_id = generate_user_id(seedval, users)
            limit = generate_limit(seedval)
            self.test_success_params.append(
                {
                    INPUT: {
                        "seedval": seedval,
                        "ingredients": ingredients,
                        "users": users,
                        "saved_ingredients": saved_ingredients,
                        "user_id": user_id,
                        "limit": limit,
                    },
                    EXPECTED_OUTPUT: get_expected_output(
                        user_id, saved_ingredients, ingredients, limit
                    ),
                }
            )

    # pylint: disable=(C0103)
    # disabled snake case error
    def runTest(self):
        print("\033[0;33m===== TEST: GetRecommendedUserIngredients =====\033[0m")
        init_app_module_dir()
        import app

        # If the below comment is not present,
        # pylance will generate an import warning.
        # We know the import is valid because the
        # above function call injects the required module directory.
        # pyright: reportMissingImports=false

        # pylint: disable=(C0200)
        # disabled consider
        # using error
        app.init_app()
        total_test_amount = len(self.test_success_params)
        for current_test_index in range(0, len(self.test_success_params)):
            test = self.test_success_params[current_test_index]
            # pylint: disable=(C0301)
            # disabled the above error
            # being line below is
            # too long, it
            # has to be in one line as a print statement
            print(
                f"\033[0;33m----- Executing test {current_test_index + 1} of {total_test_amount} -----\033[0m"
            )
            print("Injecting test data...")
            app.db.add_ingredients(test[INPUT]["ingredients"].values())
            app.db.add_google_users(test[INPUT]["users"].values())
            app.db.add_saved_ingredients(test[INPUT]["saved_ingredients"])

            validation = False
            try:
                print("Validating...")
                validation = validate_input(
                    app.db.get_recommended_ingredients_from_user(
                        test[INPUT]["user_id"], test[INPUT]["limit"]
                    ),
                    test[EXPECTED_OUTPUT],
                )
            # pylint: disable=(W0702)
            # disabled except error
            # as this except case works
            except:
                pass
            finally:
                print("Deleting test data...")
                for user in test[INPUT]["users"].keys():
                    app.db.delete_user(user)
                for ingredient in test[INPUT]["ingredients"].keys():
                    app.db.delete_ingredient(ingredient)

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
