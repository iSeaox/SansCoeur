const socket = io({
    withCredentials: true
});
socket.emit('request_game_info');

// Constantes pour le statut de la partie
const GAME_STATUS_WAITING = 0;
const GAME_STATUS_PLAYING = 1;
const GAME_STATUS_END = 2;

const ROUND_STATE_SETUP = 0
const ROUND_STATE_PLAYING = 1

// Fonction pour traduire le statut de la partie
function getGameStatusText(status) {
    switch (status) {
        case GAME_STATUS_WAITING:
            return 'En attente de joueurs';
        case GAME_STATUS_PLAYING:
            return 'En cours';
        case GAME_STATUS_END:
            return 'Terminée';
        default:
            return 'Statut inconnu';
    }
}

function getRoundStatusText(state) {
    console.log(state)
    switch (state) {
        case ROUND_STATE_SETUP:
            return 'Distribution';
        case ROUND_STATE_PLAYING:
            return 'Jouez !';
        default:
            return 'Statut inconnu';
    }
}

const CARD_COLOR_SPADES = 0
const CARD_COLOR_HEARTS = 1
const CARD_COLOR_DIAMONDS = 2
const CARD_COLOR_CLUBS = 3

function getSuitName(suit) {
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

// Éléments du DOM
const gameSection = document.getElementById('gameSection');
const teamSelect = document.getElementById('team');
const joinBtn = document.getElementById('joinBtn');
const gameInfoDiv = document.getElementById('gameInfo');
const roundInfoDiv = document.getElementById('roundInfo');
const cardTableDiv = document.getElementById('cardTable');
const startGameSection = document.getElementById('startGameSection');
const startGameBtn = document.getElementById('startGameBtn');

// Gestionnaire pour rejoindre une partie
joinBtn.addEventListener('click', () => {
    const team = parseInt(teamSelect.value);

    // Envoie la team au serveur
    socket.emit('join_game', { team });
});

// Gestionnaire pour lancer la partie
startGameBtn.addEventListener('click', () => {
    socket.emit('start_game');  // Envoie une demande de lancement de partie
});

socket.on('game_info', (data) => {
    // Affiche les informations de la partie
    gameInfoDiv.innerHTML = `
        <p>Statut de la partie : ${getGameStatusText(data.status)}</p>
        <p>Prêt à lancer : ${data.readyToStart ? "Oui" : "Non"}</p>
        <ul>
            ${data.players.map(player => `
                <li>${player.name} (Team ${player.team ?? 'Non définie'})</li>
            `).join('')}
        </ul>
    `;

    // Affiche ou masque le bouton "Lancer la partie"
    startGameSection.style.display = data.readyToStart ? 'block' : 'none';
});

socket.on('round_info', (data) => {
    console.log(data)
    roundInfoDiv.innerHTML = `
        <p>Statut de la manche : ${getRoundStatusText(data.state)}</p>
        <p>Prochain à jouer : ${data.next_turn}</p>
    `;

    cardTableDiv.innerHTML = '';
    cards = data.card_on_table;
    cards.forEach((card, index) => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        cardElement.id = `card-${index}`;
        cardElement.textContent = `${card.value} de ${getSuitName(card.color)}`;
        cardTableDiv.appendChild(cardElement);
    });

    cardTableDiv.innerHTML
});

socket.on('start_game_error', (data) => {
    alert(`Erreur : ${data.message}`);
});

socket.on('connect', () => {
    console.log('Connecté au serveur');
});

// _________________________________________________________

// Élément du DOM pour afficher le deck
const deckDiv = document.getElementById('deck');

// Écouteur d'événement pour mettre à jour le deck
socket.on('update_deck', (cards) => {
    // Efface le contenu précédent
    deckDiv.innerHTML = '';

    // Affiche chaque carte
    cards.forEach((card, index) => {
        const cardElement = document.createElement('div');
        cardElement.className = 'playing-card';
        cardElement.id = `card-${index}`;
        cardElement.textContent = `${card.value} de ${getSuitName(card.color)}`;
        deckDiv.appendChild(cardElement);

        cardElement.addEventListener('click', () => {
            socket.emit('card_clicked', {"card_id": cardElement.id});
        });
    });
});


socket.on('connect', () => {
    console.log('Connecté au serveur');
});