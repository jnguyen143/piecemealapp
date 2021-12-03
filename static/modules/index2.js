import { showToast } from './Toast.js'; // eslint-disable-line import/extensions

function addIngredient(ingredientId, name, image, liked) {
  fetch('/api/user-ingredients/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ingredient: {
        id: ingredientId,
        name,
        image,
        liked,
      },
    }),
  }).then((response) => response.json()).then((response) => {
    if (response.success) {
      showToast('Successfully added ingredient');
    } else if (response.error_code === 3) {
      showToast("You've already saved that ingredient!");
    } else {
      showToast("Couldn't add ingredient at this time");
    }
  }).catch(() => {
    showToast("Couldn't add ingredient at this time");
  });
}

function addRecipe(id, name, image, summary, fullSummary) {
  fetch('/api/user-recipes/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      recipe: {
        id,
        name,
        image,
        summary,
        full_summary: fullSummary, // eslint-disable-line camelcase
      },
    }),
  }).then((response) => response.json()).then((response) => {
    if (response.success) {
      showToast('Successfully added recipe');
    } else if (response.error_code === 3) {
      showToast('You\'ve already saved that recipe!');
    } else {
      showToast('Error adding recipe');
    }
  }).catch(() => {
    showToast('Error adding recipe');
  });
}

function addIngredientButtonEvents() {
  // eslint-disable-next-line no-restricted-syntax
  for (const btn of document.getElementsByClassName('like-button')) {
    btn.addEventListener('click', (event) => {
      const id = event.target.getAttribute('ingredient-id');
      const name = event.target.getAttribute('ingredient-name');
      const image = event.target.getAttribute('ingredient-image');
      addIngredient(id, name, image, true);
    });
  }

  // eslint-disable-next-line no-restricted-syntax
  for (const btn of document.getElementsByClassName('dislike-button')) {
    btn.addEventListener('click', (event) => {
      const id = event.target.getAttribute('ingredient-id');
      const name = event.target.getAttribute('ingredient-name');
      const image = event.target.getAttribute('ingredient-image');
      addIngredient(id, name, image, false);
    });
  }
}

// eslint-disable-next-line no-restricted-syntax, no-unused-vars
document.getElementById('secretbutton').addEventListener('click', (secretevent) => {
  addIngredientButtonEvents();

  // eslint-disable-next-line no-restricted-syntax
  for (const btn of document.getElementsByClassName('add-recipe-button')) {
    btn.addEventListener('click', (event) => {
      const id = event.target.getAttribute('recipe-id');
      const name = event.target.getAttribute('recipe-name');
      const image = event.target.getAttribute('recipe-image');
      const summary = event.target.getAttribute('recipe-summary');
      const fullSummary = event.target.getAttribute('recipe-full-summary');
      addRecipe(id, name, image, summary, fullSummary);
    });
  }
});
document.getElementById('secretbutton').click();
// eslint-disable-next-line no-restricted-syntax
for (const btn of document.getElementsByClassName('delete-button')) {
  btn.addEventListener('click', (event) => {
    if (event.target.hasAttribute('ingredient-id')) {
      // Delete ingredient
      const id = event.target.getAttribute('ingredient-id');
      // const name = event.target.getAttribute('ingredient-name');
      // const image = event.target.getAttribute('ingredient-image');
      fetch('/api/delete-ingredient', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id }),
      }).then((response) => response.json()).then((response) => {
        if (response.result === 0) {
          showToast('Successfully deleted ingredient');
          window.location.href = '/profile';
        } else {
          showToast('Error deleting ingredient');
        }
      }).catch(() => {
        showToast('Error deleting ingredient');
      });
    } else {
      // Delete recipe
      const id = event.target.getAttribute('recipe-id');
      fetch('/api/delete-recipe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id }),
      }).then((response) => response.json()).then((response) => {
        if (response.result === 0) {
          showToast('Successfully deleted recipe');
          window.location.href = '/profile';
          // redirect("/profile")
        } else {
          showToast('Error deleting recipe');
        }
      }).catch(() => {
        showToast('Error deleting recipe');
      });
    }
  });
}
