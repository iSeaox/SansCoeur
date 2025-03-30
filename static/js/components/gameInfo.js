import { getGameStatusText } from "../utils.js";
import { GAME_STATUS_WAITING, GAME_STATUS_PLAYING, GAME_STATUS_END } from "../utils.js";

const gameInfoDiv = document.getElementById('gameInfo');
const startGameBtn = document.getElementById('startGameBtn');
const startGameSection = document.getElementById("startGameSection");

startGameBtn.addEventListener('click', () => {
  const startGameMaxPointInput = document.getElementById("startGameMaxPointInput");
  if (startGameMaxPointInput) {
    const inputValue = startGameMaxPointInput.value.trim();

    if (/^\d+$/.test(inputValue)) {
      socket.emit('start_game', { maxPoints: parseInt(inputValue) });
    } else {
      alert("Veuillez entrer un nombre valide.");
    }
  }
});


socket.on('game_info', (data) => {
  console.log("game_info: ", data)
  // Affiche les informations de la partie
  const readyText =
    data.status !== GAME_STATUS_PLAYING
      ? `<p>Prêt à lancer : ${data.readyToStart ? "Oui" : "Non"}</p>`
      : "";
  let scoreText = "";
  if(data.status == GAME_STATUS_PLAYING) {
    scoreText = `<p>Score: ${data.score[0]} - ${data.score[1]}</p>`;
  }
  gameInfoDiv.innerHTML = `
    <p>Statut de la partie : <br/>${getGameStatusText(data.status)}</p>
    ${readyText}
    <ul>
      ${data.players
        .map((player) => `<li>${player.name} (Team ${player.team ?? 'Non définie'})</li>`)
        .join('')}
    </ul>
    ${scoreText}
  `;



  // Affiche le bouton uniquement lorsque le jeu est en attente et prêt à démarrer
  startGameSection.style.display =
    data.readyToStart && data.status === GAME_STATUS_WAITING ? "block" : "none";
});
