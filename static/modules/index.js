import { showToast } from './Toast.js';

for (let btn of document.getElementsByClassName("add-button")) {
    btn.addEventListener("click", () => {
        showToast("You need to be logged in to save recipes and ingredients", 6000);
    });
}