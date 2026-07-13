function createMessageBadge(data) {
  console.log(data);
  const chatContainer = document.getElementById("chat-messages");
  const playerNameH = document.getElementById("username");
  let username = "undefined";
  if (playerNameH) {
    username = playerNameH.innerHTML.toLowerCase();
  }

  const badgeContainer = document.createElement("div");
  badgeContainer.className = `text-${(data.player == username ? "end" : "start")} mb-2`;

  const badgeLabel = document.createElement("div");
  badgeLabel.className = "chat-username text-muted";
  badgeLabel.textContent = `${data.player} - ${data.time}`;
  badgeContainer.appendChild(badgeLabel);

  // Si le message contient une URL de GIF on affiche une iframe :)
  if (data.gif_url) {
    if (data.gif_url.includes("giphy.com/embed/")) {
      const iframe = document.createElement("iframe");
      iframe.src = data.gif_url;
      iframe.width = "250";
      iframe.height = "200";
      iframe.frameBorder = "0";
      iframe.allowFullscreen = true;
      badgeContainer.appendChild(iframe);
    } else {
      const gifImage = document.createElement("img");
      gifImage.src = data.gif_url;
      gifImage.alt = "GIF qui marche pas";
      gifImage.style.maxWidth = "200px";
      badgeContainer.appendChild(gifImage);
    }
  } else {
    const badgeBody = `<span class="badge fs-6 text-wrap text-start msg-${
      data.player.toLowerCase() === username ? "perso" : "other"
    } ${"spec" in data ? "spec": ""}">${data.message}</span>`;
    badgeContainer.insertAdjacentHTML("beforeend", badgeBody);
  }
  return badgeContainer;
}

document.getElementById("chat-form").addEventListener("submit", function (event) {
  event.preventDefault();
  const messageInput = document.getElementById("message-input");
  let message = messageInput.value;
  if (message.trim() !== "") {
    let embedUrl = "";

    if (message.includes("giphy.com")) {
      let id = "";
      try {
        const urlObj = new URL(message);
        const segments = urlObj.pathname.split("/").filter((segment) => segment !== "");
        const lastSegment = segments[segments.length - 1] || "";
        id = lastSegment.includes("-") ? lastSegment.split("-").pop() : lastSegment;
      } catch (error) {
        const parts = message.split("-");
        id = parts[parts.length - 1];
      }
      embedUrl = "https://giphy.com/embed/" + id;
    }

    if (embedUrl) {
      socket.emit("chat_message", { gif_url: embedUrl });
    } else {
      socket.emit("chat_message", { message: message });
    }
    messageInput.value = "";
  }
});

socket.on("receive_chat_message", (data) => {
  const chatDiv = document.getElementById("chat-messages");
  const maxMessage = 16;
  if (chatDiv.childNodes.length >= maxMessage) {
    chatDiv.removeChild(chatDiv.firstElementChild);
  }
  chatDiv.appendChild(createMessageBadge(data));
  chatDiv.scrollTop = chatDiv.scrollHeight;
});

socket.on("receive_chat_gif", (data) => {
  const chatDiv = document.getElementById("chat-messages");
  const maxMessage = 16;
  if (chatDiv.childNodes.length >= maxMessage) {
    chatDiv.removeChild(chatDiv.firstElementChild);
  }
  chatDiv.appendChild(createMessageBadge(data));
  chatDiv.scrollTop = chatDiv.scrollHeight;
});


import CONFIG from '../config/config.js';

// Constantes pour l'API Giphy
const GIPHY_SEARCH_URL = "https://api.giphy.com/v1/gifs/search";

// Sélecteurs DOM
const gifButton = document.getElementById("gif-button");
const gifSelector = document.getElementById("gif-selector");
const gifSearch = document.getElementById("gif-search");
const gifResults = document.getElementById("gif-results");

// État
let searchTimeout = null;

// Fonction pour rechercher des GIFs
function searchGifs(query = "") {
  const url = new URL(GIPHY_SEARCH_URL);
  url.searchParams.append("q", query || "looser");
  url.searchParams.append("api_key", CONFIG.GIPHY_API_KEY);
  url.searchParams.append("limit", CONFIG.GIF_LIMIT);
  url.searchParams.append("rating", CONFIG.GIPHY_RATING);

  fetch(url)
    .then(response => response.json())
    .then(data => {
      displayGifs(data.data || []);
    })
    .catch(error => {
      console.error("Erreur lors de la recherche de GIFs:", error);
    });
}

// Fonction pour afficher les GIFs
function displayGifs(results) {
  gifResults.innerHTML = "";

  results.forEach(result => {
    const gifItem = document.createElement("div");
    gifItem.className = "gif-item";

    const img = document.createElement("img");
    img.src = result.images.fixed_width_small.url; // Une version miniature pour l'aperçu
    img.alt = result.title;

    gifItem.appendChild(img);
    gifResults.appendChild(gifItem);

    // Quand l'utilisateur clique sur un GIF
    gifItem.addEventListener("click", () => {
      const embedId = result.id;
      const embedUrl = "https://giphy.com/embed/" + embedId;

      // Envoyer le GIF au chat
      socket.emit("chat_message", { gif_url: embedUrl });

      // Fermer le sélecteur de GIF
      gifSelector.classList.add("d-none");
    });
  });
}

// Écouteurs d'événements
gifButton.addEventListener("click", () => {
  if (gifSelector.classList.contains("d-none")) {
    gifSelector.classList.remove("d-none");
    searchGifs(); // Charger des GIFs par défaut
  } else {
    gifSelector.classList.add("d-none");
  }
});

gifSearch.addEventListener("input", (e) => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  
  searchTimeout = setTimeout(() => {
    searchGifs(e.target.value);
  }, 300); // Délai pour éviter trop de requêtes
});

// Fermer le sélecteur si on clique ailleurs
document.addEventListener("click", (e) => {
  if (!gifSelector.contains(e.target) && e.target !== gifButton) {
    gifSelector.classList.add("d-none");
  }
});