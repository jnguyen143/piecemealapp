"""
This file tests the functionality of `database.Database.get_recommended_user_ingredients()`.

This file injects a random number of randomly generated users, ingredients,
and saved ingredients, then tests to ensure that `get_recommended_user_ingredients()`
returns the expected result given the ID of a user from the list of dummy users.
"""

import unittest
from random import randrange, seed, randint
from .... import app


INPUT = "input"
EXPECTED_OUTPUT = "expected"


def generate_prefixed_string(prefix):
    """
    Returns a randomly generated string with the specified prefix.
    """
    result = prefix
    for _ in range(1, 10):
        result += str(randint(0, 9))
    return result


def generate_ingredient():
    """
    Generates a random ingredient.
    """
    ingredient_id = randint(0, 100000)
    name = generate_prefixed_string("saved_ingredient_")
    image = generate_prefixed_string("image_")
    return {"id": ingredient_id, "name": name, "image": image}


def generate_ingredients(seedval):
    """
    Generates a random list of ingredients.
    """
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 10)):
        ingredient = generate_ingredient()
        if ingredient["id"] in result:
            continue
        result[ingredient["id"]] = ingredient
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
    Generates a list of random users.
    """
    seed(seedval)
    result = {}
    for _ in range(0, randint(0, 10)):
        user = generate_user()
        if user["id"] in result or emails_match(result, user):
            continue
        result[user["id"]] = user
    return result


def generate_saved_ingredient(users, ingredients):
    """
    Generates a random saved ingredient.
    """
    user_ids = list(users.keys())
    ingredient_ids = list(ingredients.keys())
    user_id_idx = randrange(0, len(users))
    ingredient_id_idx = randrange(0, len(ingredients))
    return {
        "user_id": user_ids[user_id_idx],
        "ingredient_id": ingredient_ids[ingredient_id_idx],
    }


def generate_saved_ingredients(seedval, users, ingredients):
    """
    Generates a random list of saved ingredients.
    """
    seed(seedval)
    result = []
    if len(ingredients) == 0:
        return []
    for _ in range(0, randint(1, len(ingredients))):
        result.append(generate_saved_ingredient(users, ingredients))
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


def get_expected_output(user_id, saved_ingredients, ingredients, limit):
    """
    Generates the expected output for the test.
    """
    actual_ingredients = []
    for saved_ingredient in saved_ingredients:
        if saved_ingredient["user_id"] == user_id:
            actual_ingredients.append(ingredients[saved_ingredient["ingredient_id"]])

    return actual_ingredients[-limit:]


def ingredients_match(mock_ingredient, db_ingredient):
    """
    Returns true if the two ingredients match.
    """
    return (
        db_ingredient.id == mock_ingredient["id"]
        and db_ingredient.name == mock_ingredient["name"]
        and db_ingredient.image == mock_ingredient["image"]
    )


def contains_ingredient(expected_output, target):
    """
    Returns true if the expected output contains the target.
    """
    for ingredient in expected_output:
        if ingredients_match(ingredient, target):
            return True
    return False


def validate_input(actual_output, expected_output):
    """
    Returns true if the actual output matches the expected output.
    """
    for output in actual_output:
        if not contains_ingredient(expected_output, output):
            return False
    return True


class GetRecommendedUserIngredientsTestCase(unittest.TestCase):
    """
    The class which holds the actual test case.
    """

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def setUp(self):
        """
        Sets up test data.
        """
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

    # pylint: disable=invalid-name
    # This name cannot conform to snake case due to the requirements from the parent class.
    def runTest(self):
        """
        Runs the test.
        """
        print("\033[0;33m===== TEST: GetRecommendedUserIngredients =====\033[0m")
        app.init_app()
        total_test_amount = len(self.test_success_params)
        for current_test_index, _ in enumerate(self.test_success_params):
            test = self.test_success_params[current_test_index]
            print(
                f"""\033[0;33m----- Executing test {current_test_index + 1} \
of {total_test_amount} -----\033[0m
                """
            )
            print("Injecting test data...")
            validation = False
            try:
                app.DATABASE.add_users(test[INPUT]["users"].values())
                app.DATABASE.add_ingredient_infos(test[INPUT]["ingredients"].values())

                ingredient_infos = []
                user_ids = []
                liked = []
                for ing in test[INPUT]["saved_ingredients"]:
                    ingredient_infos.append(
                        test[INPUT]["ingredients"][ing["ingredient_id"]]
                    )
                    user_ids.append(ing["user_id"])
                    liked.append(True)

                app.DATABASE.add_ingredients(user_ids, ingredient_infos, liked)

                print("Validating...")
                validation = validate_input(
                    app.DATABASE.get_user_top_ingredients(
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
                app.DATABASE.delete_ingredient_infos(list(test[INPUT]["ingredients"]))

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
