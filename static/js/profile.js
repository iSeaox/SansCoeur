import { sendToast } from "./utils.js";

window.socket = io({
    withCredentials: true
});

const ctx5 = document.getElementById('chart-tp-5').getContext('2d');

socket.on('stat_update', (data) => {
    if( data.type == 5) {
        const myChart = new Chart(ctx5, data.data);
    }
});

document.addEventListener("DOMContentLoaded", function () {
  // Animation du titre comme sur la page de login
  const titleElement = document.querySelector(".title");
  const text = titleElement.textContent;
  titleElement.innerHTML = "";
  for (let i = 0; i < text.length; i++) {
    const span = document.createElement("span");
    span.textContent = text[i] === " " ? "\u00A0" : text[i];
    span.style.setProperty("--i", i);
    titleElement.appendChild(span);
  }

  // Capitaliser le nom d'utilisateur
  const usernameParagraph = document.querySelector(".info-group:first-child p");
  if (usernameParagraph) {
    const username = usernameParagraph.textContent;
    socket.emit('request_stat_update', {"type": 5, "player": username});
    const capitalizedUsername =
      username.charAt(0).toUpperCase() + username.slice(1);
    usernameParagraph.textContent = capitalizedUsername;
  }

  // Any other profile-related functionality can be added here
});

function showPasswordChangeToast() {
  sendToast("Pour changer votre mot de passe contactez un admin", "danger");
}

// Make the function available globally
window.showPasswordChangeToast = showPasswordChangeToast;
