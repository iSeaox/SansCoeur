function createMessageBadge(message, player, time) {
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
    badgeLabel.textContent = player + " - " + time;
    badgeContainer.appendChild(badgeLabel);

    const badgeBody = `<span class="badge fs-6 text-wrap text-start msg-${(player == username ? "perso" : "other")}">${message}</span>`;
    badgeContainer.insertAdjacentHTML('beforeend', badgeBody);

    return badgeContainer;

}

document.getElementById('chat-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const messageInput = document.getElementById('message-input');
    const message = messageInput.value;

    if (message.trim() !== '') {
        socket.emit("chat_message", {"message": message});
        messageInput.value = '';
    }
});
socket.on('receive_chat_message', (data) => {
    const chatDiv = document.getElementById("chat-messages");
    const numberOfMessage = Array.from(chatDiv.childNodes)
        .filter(node => node.nodeType === Node.ELEMENT_NODE && node.tagName === 'DIV').length;

    const maxMessage = 6;
    if (numberOfMessage >= maxMessage) {
        console.log(numberOfMessage)
        chatDiv.removeChild(chatDiv.firstElementChild);
    }
    chatDiv.appendChild(createMessageBadge(data.message, data.player, data.time));


});

