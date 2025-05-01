import { sendToast } from "../utils.js";

window.socket = io({
  withCredentials: true
});

window.admin_socket = io("/admin", {
  withCredentials: true
});

// Fonction pour récupérer la liste des joueurs
function fetchPlayersList() {
  admin_socket.emit("get_players");
}

// Fonction pour créer les lignes de la table des joueurs
function renderPlayersList(players) {
  const playersListElement = document.getElementById("players-list");

  if (!players || players.length === 0) {
    playersListElement.innerHTML = `
      <tr>
        <td colspan="5" class="text-center">Aucun joueur trouvé</td>
      </tr>
    `;
    return;
  }

  playersListElement.innerHTML = players.map(player => `
    <tr>
      <td>
        ${player.username}
        ${player.is_admin ? '<span class="badge bg-danger ms-2">Admin</span>' : ''}
      </td>
      <td>${player.registered_on}</td>
      <td>${player.last_login}</td>
      <td>${player.password_needs_update}</td>
      <td>
        <div class="btn-group btn-group-sm" role="group">
          <button type="button" class="btn btn-unlock" data-username="${player.username}" onclick="unlockPassword('${player.username}')">
            <i class="bi bi-person-raised-hand text-white"></i>
          </button>
          <button type="button" class="btn btn-delete" data-username="${player.username}" onclick="confirmDeletePlayer('${player.username}')">
            <i class="bi bi-trash-fill text-white"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join('');
}

// Écouter l'événement de réception de la liste des joueurs
admin_socket.on("players_list", data => {
  console.log("Received players data:", data);
  renderPlayersList(data.players);
});

// Fonctions pour les actions sur les joueurs (à implémenter plus tard)
window.unlockPassword = function(username) {
  admin_socket.emit("update_flag", { username });
};

window.confirmDeletePlayer = function(username) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer le joueur ${username} ?`)) {
    admin_socket.emit("delete_player", { username });
  }
};

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

  // Ajouter l'événement de clic sur le bouton de rafraîchissement
  const refreshButton = document.getElementById("refresh-players");
  if (refreshButton) {
    refreshButton.addEventListener("click", fetchPlayersList);
  }

  // Charger initialement la liste des joueurs
  fetchPlayersList();
});

const btnAddPlayer = document.getElementById("add-player");
const textAddPlayer = document.getElementById("new-player-name");

btnAddPlayer.addEventListener("click", function () {
  const username = textAddPlayer.value.trim();
  if (username) {
    admin_socket.emit("add_player", { username });
    textAddPlayer.value = "";
  } else {
    sendToast("Veuillez entrer un nom d'utilisateur valide.", "danger");
  }
});