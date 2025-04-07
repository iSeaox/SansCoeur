function createMessageBadge(data) {
  const chatContainer = document.getElementById("chat-messages");
  const playerNameH = document.getElementById("username");
  let username = "undefined";
  if (playerNameH) {
    username = playerNameH.innerHTML.toLowerCase();
  }

  const badgeContainer = document.createElement("div");
    badgeContainer.className = `text-${(player == username ? "end" : "start")} mb-2`;

  const badgeLabel = document.createElement("div");
  badgeLabel.className = "chat-username text-muted";
  badgeLabel.textContent = data.player + " - " + data.time;
  badgeContainer.appendChild(badgeLabel);

  // Si le message contient une URL de GIF on affiche une iframe :)
  if (data.gif_url) {
    if (data.gif_url.includes("tenor.com/embed/")) {
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
      gifImage.alt = "GIF envoyé par " + data.player;
      gifImage.style.maxWidth = "200px";
      badgeContainer.appendChild(gifImage);
    }
  } else {
    const badgeBody = `<span class="badge fs-6 text-wrap text-start msg-${
      data.player.toLowerCase() === username ? "perso" : "other"
    }">${data.message}</span>`;
    badgeContainer.insertAdjacentHTML("beforeend", badgeBody);
  }
  return badgeContainer;
}

document.getElementById("chat-form").addEventListener("submit", function (event) {
  event.preventDefault();
  const messageInput = document.getElementById("message-input");
  let message = messageInput.value;
  if (message.trim() !== "") {
    if (message.includes("tenor.com/view/")) {
      // "https://tenor.com/view/nom-du-gif-xxxxxxx"
      const parts = message.split("-");
      const id = parts[parts.length - 1];
      const embedUrl = "https://tenor.com/embed/" + id;
      socket.emit("chat_message", { gif_url: embedUrl });
    } else {
      socket.emit("chat_message", { message: message });
    }
    messageInput.value = "";
  }
});

socket.on("receive_chat_message", (data) => {
  const chatDiv = document.getElementById("chat-messages");
  const numberOfMessage = Array.from(chatDiv.childNodes).filter(
    (node) => node.nodeType === Node.ELEMENT_NODE && node.tagName === "DIV"
  ).length;
  const maxMessage = 6;
  if (numberOfMessage >= maxMessage) {
    chatDiv.removeChild(chatDiv.firstElementChild);
  }
  chatDiv.appendChild(createMessageBadge(data));
});

socket.on("receive_chat_gif", (data) => {
  const chatDiv = document.getElementById("chat-messages");
  const numberOfMessage = Array.from(chatDiv.childNodes).filter(
    (node) => node.nodeType === Node.ELEMENT_NODE && node.tagName === "DIV"
  ).length;
  const maxMessage = 6;
  if (numberOfMessage >= maxMessage) {
    chatDiv.removeChild(chatDiv.firstElementChild);
  }
  chatDiv.appendChild(createMessageBadge(data));
});
