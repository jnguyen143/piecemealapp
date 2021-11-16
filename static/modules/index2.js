import { showToast } from "./Toast.js";

for (let btn of document.getElementsByClassName("add-button")) {
  btn.addEventListener("click", (event) => {
    if (event.target.hasAttribute("ingredient-id")) {
      // Add ingredient
      let id = event.target.getAttribute("ingredient-id");
      let name = event.target.getAttribute("ingredient-name");
      let image = event.target.getAttribute("ingredient-image");
      fetch("/api/save-ingredient", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: id, name: name, image: image })
      }).then(response => response.json()).then(response => {
        if (response.result == 0) {
          showToast("Successfully added ingredient");
        } else {
          showToast("Error adding ingredient");
        }
      }).catch(() => {
        showToast("Error adding ingredient");
      });
    } else {
      // Add recipe
      let id = event.target.getAttribute("recipe-id");
      let name = event.target.getAttribute("recipe-name");
      let image = event.target.getAttribute("recipe-image");
      let summary = event.target.getAttribute("recipe-summary");
      let full_summary = event.target.getAttribute("recipe-full-summary");
      fetch("/api/save-recipe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          id: id,
          name: name,
          image: image,
          summary: summary,
          full_summary:
            full_summary
        })
      }).then(response => response.json()).then(response => {
        if (response.result == 0) {
          showToast("Successfully added recipe");
        } else {
          showToast("Error adding recipe");
        }
      }).catch(() => {
        showToast("Error adding recipe");
      });
    }
  });
}

for (let btn of document.getElementsByClassName("delete-button")) {
  btn.addEventListener("click", (event) => {
    if (event.target.hasAttribute("ingredient-id")) {
      // Delete ingredient
      let id = event.target.getAttribute("ingredient-id");
      let name = event.target.getAttribute("ingredient-name");
      let image = event.target.getAttribute("ingredient-image");
      fetch("/api/delete-ingredient", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: id })
      }).then(response => response.json()).then(response => {
        if (response.result == 0) {
          showToast("Successfully deleted ingredient");
          location.href = '/profile'
        } else {
          showToast("Error deleting ingredient");
        }
      }).catch(() => {
        showToast("Error deleting ingredient");
      });
    } else {
      // Delete recipe
      let id = event.target.getAttribute("recipe-id");
      fetch("/api/delete-recipe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: id })
      }).then(response => response.json()).then(response => {
        if (response.result == 0) {
          showToast("Successfully deleted recipe");
          location.href = '/profile'
          // redirect("/profile")
        } else {
          showToast("Error deleting recipe");
        }
      }).catch(() => {
        showToast("Error deleting recipe");
      });
    }
  });
}