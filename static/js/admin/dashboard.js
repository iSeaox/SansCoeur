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