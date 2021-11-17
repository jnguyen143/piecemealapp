import { showToast } from './Toast.js'; // eslint-disable-line import/extensions

// eslint-disable-next-line no-restricted-syntax
for (const btn of document.getElementsByClassName('add-button')) {
  btn.addEventListener('click', (event) => {
    if (event.target.hasAttribute('ingredient-id')) {
      // Add ingredient
      const id = event.target.getAttribute('ingredient-id');
      const name = event.target.getAttribute('ingredient-name');
      const image = event.target.getAttribute('ingredient-image');
      fetch('/api/save-ingredient', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id, name, image }),
      }).then((response) => response.json()).then((response) => {
        if (response.result === 0) {
          showToast('Successfully added ingredient');
        } else {
          showToast('Error adding ingredient');
        }
      }).catch(() => {
        showToast('Error adding ingredient');
      });
    } else {
      // Add recipe
      const id = event.target.getAttribute('recipe-id');
      const name = event.target.getAttribute('recipe-name');
      const image = event.target.getAttribute('recipe-image');
      const summary = event.target.getAttribute('recipe-summary');
      const full_summary = event.target.getAttribute('recipe-full-summary'); // eslint-disable-line camelcase
      fetch('/api/save-recipe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id,
          name,
          image,
          summary,
          full_summary, // eslint-disable-line camelcase
        }),
      }).then((response) => response.json()).then((response) => {
        if (response.result === 0) {
          showToast('Successfully added recipe');
        } else {
          showToast('Error adding recipe');
        }
      }).catch(() => {
        showToast('Error adding recipe');
      });
    }
  });
}

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
