import { encryptData } from './EncryptedRequests.js'; // eslint-disable-line
import { showToast } from './Toast.js'; // eslint-disable-line

async function startSignup(data) {
  return fetch('/api/signup/init', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/octet-stream',
    },
    body: data,
  });
}

document.getElementById('default-signup-form').onsubmit = () => {
  password = document.getElementById("password")
  passwordCheck = document.getElementById("passwordConfirm")
  if (password != passwordCheck) {
    showToast("Passwords must match!")
  }

  // Encrypt the data, then send it to the server
  encryptData(JSON.stringify({
    authentication: 0,
    username: document.getElementById('username').value,
    email: document.getElementById('email').value,
    given_name: document.getElementById('given_name').value,
    family_name: document.getElementById('family_name').value,
    password: document.getElementById('password').value,
  })).then((data) => {
    startSignup(data).then((response) => response.json()).then((response) => {
      if (response.success) { window.location.href = '/'; } else {
        showToast('Failed to sign up - Invalid credentials');
      }
    });
  }).catch(() => {
    showToast('Failed to sign up - Internal server error');
  });

  return false;
};

document.getElementById('google-signup-form').onsubmit = () => {
  encryptData(JSON.stringify({
    authentication: 1,
  })).then((data) => {
    startSignup(data).then((response) => response.json()).then((response) => {
      if (response.success) { window.location.replace(response.redirect_url); } else {
        showToast('Failed to sign up - Invalid credentials');
      }
    });
  }).catch(() => {
    showToast('Failed to sign up - Internal server error');
  });

  return false;
};
const email = document.getElementById('email');
const emailError = document.querySelector('#mail + span.error');



email.addEventListener('input', function (event) {
  if (email.validity.valid) {
    emailError.textContent = ''; // Reset the content of the message
    emailError.className = 'error'; // Reset the visual state of the message
  } else {
    showError();
  }
});


form.addEventListener('submit', function (event) {
  if (!email.validity.valid) {
    showError();
    event.preventDefault();
  }
});

function showError() {
  if (email.validity.valueMissing) {
    emailError.textContent = 'You need to enter an e-mail address.';
  }
  else if (email.validity.typeMismatch) {
    emailError.textContent = 'Entered value needs to be an e-mail address.';
  }
  emailError.className = 'error active';
}

var Password = document.getElementById("password");
var letter = document.getElementById("letter");
var capital = document.getElementById("capital");
var number = document.getElementById("number");
var length = document.getElementById("length");

Password.onfocus = function () {
  document.getElementById("message").style.display = "block";
}
Password.onblur = function () {
  document.getElementById("message").style.display = "none";
}

Password.onkeyup = function () {
  // Validate lowercase letters
  var lowerCaseLetters = /[a-z]/g;
  if (Password.value.match(lowerCaseLetters)) {
    letter.classList.remove("invalid");
    letter.classList.add("valid");
  } else {
    letter.classList.remove("valid");
    letter.classList.add("invalid");
  }
  var upperCaseLetters = /[A-Z]/g;
  if (Password.value.match(upperCaseLetters)) {
    capital.classList.remove("invalid");
    capital.classList.add("valid");
  } else {
    capital.classList.remove("valid");
    capital.classList.add("invalid");
  }

  // Validates numbers in password  
  var numbers = /[0-9]/g;
  if (Password.value.match(numbers)) {
    number.classList.remove("invalid");
    number.classList.add("valid");
  } else {
    number.classList.remove("valid");
    number.classList.add("invalid");
  }
  // Validates length of password
  if (Password.value.length >= 8) {
    length.classList.remove("invalid");
    length.classList.add("valid");
  } else {
    length.classList.remove("valid");
    length.classList.add("invalid");
  }
}