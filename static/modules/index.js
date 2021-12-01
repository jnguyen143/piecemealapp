import { showToast } from './Toast.js';

for (let btn of document.getElementsByClassName("add-button")) {
  btn.addEventListener("click", () => {
    showToast("You need to be logged in to save recipes and ingredients", 6000);
  });
}




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

