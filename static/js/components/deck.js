const deckDiv = document.getElementById('deck');

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