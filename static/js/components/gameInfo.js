import { getGameStatusText } from "../utils.js";
import { GAME_STATUS_WAITING, GAME_STATUS_PLAYING, GAME_STATUS_END } from "../utils.js";

const gameInfoDiv = document.getElementById('gameInfo');
const startGameBtn = document.getElementById('startGameBtn');
const quitGameSection = document.getElementById('quitGameSection');
const quitGameBtn = document.getElementById('quitGameBtn');
const startGameSection = document.getElementById("startGameSection");
const scoreTableDiv = document.getElementById("scoreTable");

quitGameBtn.addEventListener('click', () => {
  socket.emit('quit_game');
})

socket.on('quit_success', () => {
  window.location.href = '/';
});

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

    scoreTableDiv.innerHTML = ''; // Clear previous scores
    if("round_score" in data) {
      data.round_score.forEach(item => {
        const scoreTeam0 = item.score[0];
        const scoreTeam1 = item.score[1];
        const talkValue = item.talk.value;
        const team = item.talk.team;

        // Créer les éléments pour les scores
        const scoreElement = document.createElement('div');
        scoreElement.classList.add('score');
        let scoreTeam0Color = '';
        let scoreTeam1Color = '';
        if (team == 0) {
          scoreTeam0Color = (scoreTeam0 < 81 || scoreTeam0 < talkValue) ? 'loose' : 'win';
        }
        else {
          scoreTeam1Color = (scoreTeam1 < 81 || scoreTeam1 < talkValue) ? 'loose' : 'win';
        }

        // Ajouter le score dans le format demandé
        scoreElement.innerHTML = `
          <span class="${scoreTeam0Color}">${scoreTeam0}</span> -
          <span class="${scoreTeam1Color}">${scoreTeam1}</span>
        `;
        scoreTableDiv.appendChild(scoreElement);
      });
    }
  }
  gameInfoDiv.innerHTML = `
    <p>Statut de la partie : <br/>${getGameStatusText(data.status)}</p>
    ${readyText}
    <ul>
      ${data.players
        .map((player) => `<li>${player.name} <span class="${player.team === 1 ? 'bg-team-1' : 'bg-team-0'}">Team ${player.team ?? 'Non définie'}</span></span></li>`)
        .join('')}
    </ul>
    ${scoreText}
  `;

  if(data.status === GAME_STATUS_WAITING) {
    if("last_game_data" in data) {
      const players = data.last_game_data.players;
      const scores = data.last_game_data.score;

      const team0Players = players.filter(player => player.team === 0);
      const team1Players = players.filter(player => player.team === 1);
      gameInfoDiv.innerHTML += `<hr style="margin: 5% 20% 5% 20%">
          <p>Dernière partie :</p>`
      gameInfoDiv.innerHTML += `${team0Players[0].name} - ${team0Players[1].name} : ${scores[0]}<br>`
      gameInfoDiv.innerHTML += `${team1Players[0].name} - ${team1Players[1].name} : ${scores[1]}`
    }
  }

    if(quitGameSection) {
      if(data.status === GAME_STATUS_WAITING) {
        quitGameSection.className = quitGameSection.className.replace(/\bd-none\b/g, 'd-flex');
      }
      else {
        quitGameSection.className = quitGameSection.className.replace(/\bd-flex\b/g, 'd-none');
      }
    }

  // Affiche le bouton uniquement lorsque le jeu est en attente et prêt à démarrer
  if (startGameSection) {
    if(data.readyToStart && data.status === GAME_STATUS_WAITING) {
      startGameSection.className = startGameSection.className.replace(/\bd-none\b/g, 'd-flex');
    }
    else {
      startGameSection.className = startGameSection.className.replace(/\bd-flex\b/g, 'd-none');
    }
  }
});
