import { showToast } from './Toast.js';

// for (let btn of document.getElementsByClassName("add-button")) {
//   btn.addEventListener("click", () => {
//     showToast("You need to be logged in to save recipes and ingredients", 6000);
//   });
// }

// eslint-disable-next-line no-restricted-syntax, no-unused-vars 
document.getElementById('secretbutton').addEventListener('click', (secretevent) => {

  // eslint-disable-next-line no-restricted-syntax
  for (const btn of document.getElementsByClassName('add-recipe-button')) {
    btn.addEventListener('click', (event) => {
      // console.log("hihi")
      showToast("You need to be logged in to save recipes and ingredients", 6000);
    });
  }
  for (const btn of document.getElementsByClassName('recipe-link')) {
    btn.addEventListener('click', (event) => {
      // console.log("hihi")
      const url = event.target.getAttribute("recipe-card-url");
      cardModal(url);
      return false;
    });
  }
  addIngredientButtonEvents();

});

function addIngredientButtonEvents() {
  // eslint-disable-next-line no-restricted-syntax
  for (const btn of document.getElementsByClassName('like-button')) {
    btn.addEventListener('click', (event) => {
      showToast("You need to be logged in to like ingredients", 6000);
    });
  }

  // eslint-disable-next-line no-restricted-syntax
  for (const btn of document.getElementsByClassName('dislike-button')) {
    btn.addEventListener('click', (event) => {
      showToast("You need to be logged in to dislike ingredients", 6000);
    });
  }
}

document.getElementById('secretbutton').click();

// function searchRecipes() {
//   // eslint-disable-next-line no-restricted-syntax
//   for (const btn of document.getElementsByClassName('search')) {
//     btn.addEventListener('click', (event) => {
//       const searchRecipes = event.target.getAttribute('searchRecipes');
//       fetch('/api/recipe-info/search', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({ user_id: userId }),
//       }).then((response) => response.json()).then((response) => {
//         if (response.result !== 0) { showToast('Failed to delete friend'); } else {
//           gotoPage('search_recipes').then(() => searchRecipes()).then(() => showToast('Successfully deleted friend'));
//         }
//       }).catch(() => showToast('Failed to delete friend'));
//     });
//   }
// }

