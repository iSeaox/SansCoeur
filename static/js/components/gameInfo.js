import { getGameStatusText } from "../utils.js";
import { GAME_STATUS_WAITING, GAME_STATUS_PLAYING, GAME_STATUS_END } from "../utils.js";

const gameStatusDiv = document.getElementById("gameStatusInfo");
const scoreInfoDiv = document.getElementById("scoreInfo");
const lastGameInfoDiv = document.getElementById("lastGameInfo");
const startGameBtn = document.getElementById("startGameBtn");
const quitGameSection = document.getElementById("quitGameSection");
const quitGameBtn = document.getElementById("quitGameBtn");
const startGameSection = document.getElementById("startGameSection");
const scoreTableDiv = document.getElementById("scoreTable");

let lastGameInfoData = null;

quitGameBtn.addEventListener("click", () => {
  socket.emit("quit_game");
});
socket.on("quit_success", () => {
  window.location.href = "/";
});

startGameBtn.addEventListener("click", () => {
  const startGameMaxPointInput = document.getElementById("startGameMaxPointInput");
  if (startGameMaxPointInput) {
    const inputValue = startGameMaxPointInput.value.trim();
    if (/^\d+$/.test(inputValue)) {
      socket.emit("start_game", { maxPoints: parseInt(inputValue) });
    } else {
      alert("Veuillez entrer un nombre valide.");
    }
  }
});

socket.on("game_info", (data) => {
  console.log("game_info: ", data);

  const team0Players = data.players.filter((player) => player.team === 0);
  const team1Players = data.players.filter((player) => player.team === 1);
  const leftSideDiv = document.querySelector(".left-side");
  const rightSideDiv = document.querySelector(".right-side");

  leftSideDiv.innerHTML = team0Players.map((player) => `<div>${player.name}</div>`).join("");
  rightSideDiv.innerHTML = team1Players.map((player) => `<div>${player.name}</div>`).join("");

  // Afficher le statut et l'état de préparation
  const readyText =
    data.status !== GAME_STATUS_PLAYING
      ? `<p>Prêt à lancer : ${data.readyToStart ? "Oui" : "Non"}</p>`
      : "";
  gameStatusDiv.innerHTML = `
    <p>Statut de la partie : <br/>${getGameStatusText(data.status)}</p>
    ${readyText}
  `;

  // Affichage du score en cours
  if (data.status === GAME_STATUS_PLAYING || data.status === GAME_STATUS_END) {
    scoreInfoDiv.innerHTML = `<p>Score : ${data.score[0]} - ${data.score[1]}</p>`;
  } else {
    scoreInfoDiv.innerHTML = "";
  }

  // Affichage des scores par manche
  scoreTableDiv.innerHTML = "";
  if ("round_score" in data) {
    data.round_score.forEach((item) => {
      const scoreElement = document.createElement("div");
      scoreElement.classList.add("score");

      if (item.talk) {
        const scoreTeam0 = item.score[0];
        const scoreTeam1 = item.score[1];
        const talkValue = item.talk.value;
        const team = item.talk.team;
        let scoreTeam0Color = "";
        let scoreTeam1Color = "";
        if (team == 0) {
          scoreTeam0Color = (scoreTeam0 < 81 || scoreTeam0 < talkValue) ? 'loose' : 'win';
        }
        else {
          scoreTeam1Color = (scoreTeam1 < 81 || scoreTeam1 < talkValue) ? 'loose' : 'win';
        }
        scoreElement.innerHTML = `
          <span class="${scoreTeam0Color}">${scoreTeam0}</span> -
          <span class="${scoreTeam1Color}">${scoreTeam1}</span>
        `;
      } else {
        scoreElement.innerHTML = `<span>${item.score[0]}</span> - <span>${item.score[1]}</span>`;
      }
      scoreTableDiv.appendChild(scoreElement);
    });
  }

  // Affichage de la dernière partie
  lastGameInfoDiv.innerHTML = "";
  if (data.status === GAME_STATUS_WAITING && "last_game_data" in data) {
    const players = data.last_game_data.players;
    const scores = data.last_game_data.score;
    const team0PlayersLast = players.filter((player) => player.team === 0);
    const team1PlayersLast = players.filter((player) => player.team === 1);
    lastGameInfoDiv.innerHTML = `
      <hr style="margin: 5% 20% 5% 20%">
      <p>Dernière partie :</p>
      ${team0PlayersLast[0]?.name} - ${team0PlayersLast[1]?.name} : ${scores[0]}<br>
      ${team1PlayersLast[0]?.name} - ${team1PlayersLast[1]?.name} : ${scores[1]}
    `;
  }

  // Affichage ou masquage des sections start/quit
  if (quitGameSection) {
    if (data.status === GAME_STATUS_WAITING || data.status === GAME_STATUS_END) {
      quitGameSection.classList.replace("d-none", "d-flex");
    } else {
      quitGameSection.classList.replace("d-flex", "d-none");
    }
  }
  if (startGameSection) {
    if (data.readyToStart && data.status === GAME_STATUS_WAITING) {
      startGameSection.classList.replace("d-none", "d-flex");
    } else {
      startGameSection.classList.replace("d-flex", "d-none");
    }
  }

  if (data.status === GAME_STATUS_WAITING) {
    leftSideDiv.classList.add("animate-slide-in-left");
    rightSideDiv.classList.add("animate-slide-in-right");
  } else {
    leftSideDiv.classList.remove("animate-slide-in-left");
    rightSideDiv.classList.remove("animate-slide-in-right");
    leftSideDiv.style.transform = "translateX(0)";
    rightSideDiv.style.transform = "translateX(0)";
  }

  lastGameInfoData = data;
});

function triggerBlinkAnimation(element, blinkClass) {
  element.classList.remove(blinkClass);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      element.classList.add(blinkClass);
    });
  });

  setTimeout(() => {
    if (!element.classList.contains(blinkClass)) {
      element.classList.add(blinkClass);
    }
  }, 50);

  element.style.animation = "none";
  void element.offsetWidth;
  element.style.animation = "";

  const onSlideInEnd = (event) => {
    if (event.animationName === "slide-in-left" || event.animationName === "slide-in-right") {
      element.classList.add(blinkClass);
      element.removeEventListener("animationend", onSlideInEnd);
    }
  };
  element.addEventListener("animationend", onSlideInEnd);
}

socket.on("round_info", (roundData) => {
  if (!lastGameInfoData) return;

  const leftSideDiv = document.querySelector(".left-side");
  const rightSideDiv = document.querySelector(".right-side");

  leftSideDiv.classList.remove("blink-red");
  rightSideDiv.classList.remove("blink-blue");

  const nextPlayerName = roundData.next_talk || roundData.next_turn;
  if (nextPlayerName) {
    const playerObj = lastGameInfoData.players.find((p) => p.name === nextPlayerName);
    if (playerObj) {
      if (playerObj.team === 0) {
        triggerBlinkAnimation(leftSideDiv, "blink-red");
      } else if (playerObj.team === 1) {
        triggerBlinkAnimation(rightSideDiv, "blink-blue");
      }
    }
  }
});
