export const GAME_STATUS_WAITING = 0;
export const GAME_STATUS_PLAYING = 1;
export const GAME_STATUS_END = 2;

export const ROUND_STATE_SETUP = 0;
export const ROUND_STATE_TALKING = 1;
export const ROUND_STATE_PLAYING = 2;

export const CARD_COLOR_SPADES = 0;
export const CARD_COLOR_HEARTS = 1;
export const CARD_COLOR_DIAMONDS = 2;
export const CARD_COLOR_CLUBS = 3;

export function getGameStatusText(status) {
  switch (status) {
    case GAME_STATUS_WAITING:
      return '<span style="color: gray; font-style: italic;">En attente de joueurs...</span>';
    case GAME_STATUS_PLAYING:
      return 'En cours';
    case GAME_STATUS_END:
      return 'Terminée';
    default:
      return 'Statut inconnu';
  }
}

export function getSuitName(suit) {
  switch (suit) {
    case CARD_COLOR_SPADES:
      return 'Pique';
    case CARD_COLOR_HEARTS:
      return 'Coeur';
    case CARD_COLOR_DIAMONDS:
      return 'Carreau';
    case CARD_COLOR_CLUBS:
      return 'Trèfle';
    default:
      return 'Statut inconnu';
  }
}

export function getRoundStatusText(state) {
  switch (state) {
    case ROUND_STATE_SETUP:
      return 'Distribution';
    case ROUND_STATE_TALKING:
      return 'Parlez !';
    case ROUND_STATE_PLAYING:
      return 'Jouez !';
    default:
      return 'Statut inconnu';
  }
}

export function getFormattedTalk(data) {
  let out = data.current_talk.value.toString() + " " + getSuitName(data.current_talk.color);

  if ("contrer" in data && data.contrer) {
    out += " Contré";
  }

  if ("surcontrer" in data && data.surcontrer) {
    out += " Sur Contré";
  }

  out += " (" + data.current_talk.player + ")";

  return out;
}
export function getCardElement(card, index, player='') {
  const cardElement = document.createElement('div');
  cardElement.className = 'playing-card';
  cardElement.id = `card-${index}`;

  const imgCardElement = document.createElement('img');
  const imagePath = `static/img/${card.value}_${card.color}.png`;

  imgCardElement.src = imagePath;
  imgCardElement.alt = `${card.value} de ${getSuitName(card.color)}`;

  cardElement.appendChild(imgCardElement);

  // Ajouter le nom du joueur sous la carte
  const playerNameElement = document.createElement('div');
  playerNameElement.className = 'player-name';
  playerNameElement.textContent = player;

  cardElement.appendChild(playerNameElement);

  return cardElement;
}

export function formatLastTalks(talks) {

  function dumpTalk(t) {
    let out = t.value.toString() + " " + getSuitName(t.color);


    return out += " (" + t.player + ")";
  }

  let out = "";
  talks.forEach(function(talk) {
    console.log(talk)
    out += `<p>${dumpTalk(talk)}</p>`
  });
  return out
}

function createToast(message, category) {
  const toast = document.createElement("div");
  toast.className = `toast align-items-center text-bg-${category} border-0 mb-2`;
  toast.setAttribute("role", "alert");
  toast.setAttribute("aria-live", "assertive");
  toast.setAttribute("aria-atomic", "true");
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;
  return toast
}

export function sendToast(message, category) {
  let toastContainer = document.getElementById("toast-container");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toast-container";
    document.body.appendChild(toastContainer);
  }

  const toast = createToast(message, category);
  toastContainer.appendChild(toast);

  const bsToast = new bootstrap.Toast(toast, { delay: 2000 });
  bsToast.show();
  toast.addEventListener("hidden.bs.toast", function () {
    toast.remove();
  });
}

