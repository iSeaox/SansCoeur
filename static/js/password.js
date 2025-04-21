import { sendToast } from "./utils.js";

document.addEventListener("DOMContentLoaded", function () {
  // Form validation
  const form = document.querySelector('.login-form');
  form.addEventListener('submit', function(e) {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
      e.preventDefault();
      sendToast("Les mots de passe ne correspondent pas", "danger");
    }
  });
});
