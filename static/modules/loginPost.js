import { showToast } from './Toast.js'; // eslint-disable-line

const status = document.getElementById('login-error-div').getAttribute('status');

if (status === 1) {
  // 1 = Google error
  showToast('Failed to log in - External error', 6000);
} else if (status === 2) {
  // 2 = User does not exist
  showToast('Failed to log in - The selected account does not exist', 6000);
}
