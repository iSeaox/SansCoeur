import { getGameStatusText } from "../utils.js";
import { GAME_STATUS_PLAYING, GAME_STATUS_END } from "../utils.js";

const gameInfoDiv = document.getElementById('gameInfo');
const startGameBtn = document.getElementById('startGameBtn');
const startGameSection = document.getElementById('startGameSection');

// Gestionnaire pour lancer la partie
startGameBtn.addEventListener('click', () => {
  socket.emit('start_game');  // Envoie une demande de lancement de partie
});

socket.on('game_info', (data) => {
  // Affiche les informations de la partie
  gameInfoDiv.innerHTML = `
        <p>Statut de la partie : <br/>${getGameStatusText(data.status)}</p>
        <p>Prêt à lancer : ${data.readyToStart ? "Oui" : "Non"}</p>
        <ul>
            ${data.players.map(player => `
                <li>${player.name} (Team ${player.team ?? 'Non définie'})</li>
            `).join('')}
        </ul>
    `;

  // Affiche ou masque le bouton "Lancer la partie"
  startGameSection.style.display = data.readyToStart ? 'block' : 'none';
  if (data.status == GAME_STATUS_PLAYING || data.status == GAME_STATUS_END) {
    startGameSection.style.display = 'none';
  } else if (data.readyToStart) {
    startGameSection.style.display = 'block';
  }
});
