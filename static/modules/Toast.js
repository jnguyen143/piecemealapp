/*
This module defines a function for displaying a toast (pop-up message) at the bottom of the screen.
By including this module, you must also ensure that you include the associated "Toast.html" file by writing `{% include "Toast.html" %}` at the end of the document's body tag.
*/

/*
Shows the specified message in a toast for the specified amount of milliseconds (3000 by default).
*/
function showToast(message, duration = 3000) {
    // Get the toast DIV
    let x = document.getElementById("toast-div");
    x.innerHTML = message;

    // Add the "show" class to DIV
    x.className = "toast-show";

    // After 3 seconds, remove the show class from DIV
    setTimeout(function () { x.className = x.className.replace("toast-show", ""); }, duration);
}

export { showToast };