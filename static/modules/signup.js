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

