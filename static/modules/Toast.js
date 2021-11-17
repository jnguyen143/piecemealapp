/*
This module defines a function for displaying a toast (pop-up message) at the bottom of the screen.
By including this module, you must also ensure that you include the associated
"Toast.html" file by writing `{% include "Toast.html" %}` at the end of the document's body tag.
*/

/*
Shows the specified message in a toast for the specified amount of milliseconds (3000 by default).
*/
function showToast(message, duration = 3000) {
  // Get the toast DIV
  const x = document.getElementById('toast-div');
  x.innerHTML = message;

  // Add the "show" class to DIV
  x.className = 'toast-show';

  let seconds = duration / 1000.0;
  seconds -= 0.5; // To account for the fadeout offset of 0.5s

  x.style['-webkit-animation'] = `fadein 0.5s, fadeout 0.5s ${seconds}s`;
  x.style.animation = `fadein 0.5s, fadeout 0.5s ${seconds}s`;

  // After the specified duration, remove the show class from DIV
  setTimeout(() => { x.className = x.className.replace('toast-show', ''); }, duration);
}

export { showToast }; // eslint-disable-line
