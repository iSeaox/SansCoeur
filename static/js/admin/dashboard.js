import { sendToast, getGameStatusText } from "../utils.js";

window.socket = io({
  withCredentials: true
});

window.admin_socket = io("/admin", {
  withCredentials: true
});

function fetchPlayersList() {
  admin_socket.emit("get_players");
}

function fetchGamesList() {
  admin_socket.emit("get_games");
}

// Fonction pour récupérer la liste des connexions
function fetchConnectionsList() {
  admin_socket.emit("get_connections");
}
window.fetchGamesList = fetchGamesList;



function renderGamesList(games) {
  const gamesListElement = document.getElementById("games-list");
  if (!games || games.length === 0) {
    gamesListElement.innerHTML = `
    <tr>
      <td colspan="5" class="text-center">Aucune partie trouvée</td>
    </tr>
    `;
  }
  else {
    gamesListElement.innerHTML = games.map(game => `
      <tr>
        <td>${game.id}</td>
        <td>${game.players.length} / 4</td>
        <td>${game.score}</td>
        <td>${getGameStatusText(game.status)}</td>
        <td>
          <div class="btn-group btn-group-sm" role="group">
          <button type="button" class="btn btn-goto" data-username="${game.id}" onclick="goToGame('${game.id}')">
            <i class="bi bi-arrow-right text-white"></i>
          </button>
          <button type="button" class="btn btn-score" onclick="openModifyScoreModal('${game.id}', [${game.score}])">
            <i class="bi bi-pencil-square text-white"></i>
          </button>
          <button type="button" class="btn btn-delete" data-username="${game.id}" onclick="confirmDeleteGame('${game.id}')">
            <i class="bi bi-trash text-white"></i>
          </button>
          </div>
        </td>
      </tr>
    `).join("");
  }
}

// Function to open the modify score modal
function openModifyScoreModal(gameId, scores) {
  const modal = new bootstrap.Modal(document.getElementById('modifyScoreModal'));
  document.getElementById('modalGameId').value = gameId;
  document.getElementById('scoreTeam0').value = scores[0];
  document.getElementById('scoreTeam1').value = scores[1];
  modal.show();
}
window.openModifyScoreModal = openModifyScoreModal;

// Add event listener for saving score changes
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('saveScoreChanges').addEventListener('click', function() {
    const gameId = document.getElementById('modalGameId').value;
    const scoreTeam0 = parseInt(document.getElementById('scoreTeam0').value);
    const scoreTeam1 = parseInt(document.getElementById('scoreTeam1').value);

    if (isNaN(scoreTeam0) || isNaN(scoreTeam1) || scoreTeam0 < 0 || scoreTeam1 < 0) {
      showToast('error', 'Veuillez entrer des scores valides (nombres positifs).');
      return;
    }

    admin_socket.emit('update_score', {
      gameId: gameId,
      score: [scoreTeam0, scoreTeam1]
    });

    const modal = bootstrap.Modal.getInstance(document.getElementById('modifyScoreModal'));
    modal.hide();
  });
});


admin_socket.on("games_list", data => {
  renderGamesList(data.games);
});

window.confirmDeleteGame = function (gameID) {
  if (confirm(`Êtes-vous sûr de vouloir supprimer la partie ${gameID} ?`)) {
    admin_socket.emit("delete_game", { gameID });
  }
}

window.goToGame = function (gameId) {
  window.location.href = `/dashboard?id=${gameId}`;
}

window.newGame = function () {
  admin_socket.emit("new_game");
}


// ###########################################################################################
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

// Gestionnaire d'événement pour les connexions
admin_socket.on("connections_list", data => {
  console.log("Received connections data:", data);
  renderConnectionsList(data.connections);
});

function renderConnectionsList(connections) {
  const connectionsList = document.getElementById("connections-list");
  if (!connectionsList) return;

  // Vérifier si le dictionnaire est vide
  const hasConnections = Object.keys(connections).some(namespace => 
    Object.keys(connections[namespace]).length > 0
  );

  if (!connections || !hasConnections) {
    connectionsList.innerHTML = '<tr><td colspan="8" class="text-center">Aucune connexion active</td></tr>';
    return;
  }

  connectionsList.innerHTML = "";

  // Parcourir le dictionnaire par namespace
  for (const namespace in connections) {
    // Pour chaque namespace, parcourir les utilisateurs
    for (const username in connections[namespace]) {
      const userConnection = connections[namespace][username];

      const row = document.createElement('tr');

      // Namespace
      const namespaceCell = document.createElement('td');
      namespaceCell.textContent = namespace;
      namespaceCell.className = 'text-break';
      row.appendChild(namespaceCell);

      // Username
      const usernameCell = document.createElement('td');
      usernameCell.textContent = username;
      usernameCell.className = 'text-break';
      row.appendChild(usernameCell);

      // SID Socket.io
      const sidCell = document.createElement('td');
      sidCell.textContent = userConnection.sid_socketio || '-';
      sidCell.className = 'text-break';
      sidCell.style.wordWrap = 'break-word';
      sidCell.style.minWidth = '100px';
      sidCell.style.maxWidth = '150px';
      row.appendChild(sidCell);

      // EIO Socket.io
      const eioCell = document.createElement('td');
      eioCell.textContent = userConnection.eio_socketio || '-';
      eioCell.className = 'text-break';
      eioCell.style.wordWrap = 'break-word';
      eioCell.style.minWidth = '100px';
      eioCell.style.maxWidth = '150px';
      row.appendChild(eioCell);

      // Status
      const statusCell = document.createElement('td');
      if (userConnection.status) {
        statusCell.innerHTML = '<span class="badge bg-success">Connecté</span>';
      } else {
        statusCell.innerHTML = '<span class="badge bg-danger">Déconnecté</span>';
      }
      row.appendChild(statusCell);

      // IP Address
      const ipCell = document.createElement('td');
      ipCell.textContent = userConnection.ip_address || '-';
      ipCell.className = 'text-break';
      row.appendChild(ipCell);

      // User Agent
      const uaCell = document.createElement('td');
      uaCell.textContent = userConnection.user_agent || '-';
      uaCell.className = 'text-break';
      uaCell.style.wordWrap = 'break-word';
      uaCell.style.minWidth = '150px';
      uaCell.style.maxWidth = '200px';
      uaCell.title = userConnection.user_agent; // Ajoute un tooltip pour voir l'agent complet
      row.appendChild(uaCell);

      // Rooms
      const roomsCell = document.createElement('td');
      roomsCell.className = 'text-break';
      if (userConnection.rooms && userConnection.rooms.length) {
        const roomsList = document.createElement('ul');
        roomsList.className = 'list-unstyled mb-0';
        userConnection.rooms.forEach(room => {
          const roomItem = document.createElement('li');
          roomItem.textContent = room;
          roomItem.style.wordWrap = 'break-word';
          roomsList.appendChild(roomItem);
        });
        roomsCell.appendChild(roomsList);
      } else {
        roomsCell.textContent = '-';
      }
      row.appendChild(roomsCell);

      connectionsList.appendChild(row);
    }
  }
}

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

  fetchPlayersList();
  fetchGamesList();
  fetchConnectionsList(); // Ajouter cette ligne pour charger les connexions
  
  // Configurer les rafraîchissements périodiques
  setInterval(() => {
    fetchPlayersList();
    fetchGamesList();
    fetchConnectionsList(); // Ajouter cette ligne pour rafraîchir régulièrement
  }, 30000); // Rafraîchir toutes les 30 secondes
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

// Exposer les fonctions de récupération des connexions
window.fetchConnectionsList = fetchConnectionsList;