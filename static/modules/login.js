import { encryptData } from './EncryptedRequests.js'; // eslint-disable-line
import { showToast } from './Toast.js'; // eslint-disable-line

async function startLogin(data) {
  return fetch('/api/start-login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/octet-stream',
    },
    body: data,
  });
}

document.getElementById('default-login-form').onsubmit = () => {
  // Encrypt the data, then send it to the server
  encryptData(JSON.stringify({
    authentication: 'Default',
    username: document.getElementById('username').value,
    password: document.getElementById('password').value,
  })).then((data) => {
    startLogin(data).then((response) => response.json()).then((response) => {
      if (response.success) {
        window.location.href = '/';
      } else {
        showToast('Failed to log in - Invalid credentials');
      }
    });
  }).catch(() => {
    showToast('Failed to log in - Internal server error');
  });

  return false;
};

document.getElementById('google-login-form').onsubmit = () => {
  encryptData(JSON.stringify({ authentication: 'Google' })).then((data) => {
    startLogin(data).then((response) => response.json()).then((response) => {
      if (response.success) { window.location.replace(response.redirect_url); } else {
        showToast('Failed to log in - Invalid credentials');
      }
    });
  }).catch(() => {
    showToast('Failed to log in - Internal server error');
  });

  return false;
};
