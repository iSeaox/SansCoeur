import { getRoundStatusText, getSuitName } from "../utils.js"

const roundInfoDiv = document.getElementById('roundInfo');
const cardTableDiv = document.getElementById('cardTable');

socket.on('round_info', (data) => {
    console.log(data)
    roundInfoDiv.innerHTML = `
        <p>Statut de la manche : ${getRoundStatusText(data.state)}</p>
        <p>Prochain à jouer : ${data.next_turn}</p>
    `;


    cardTableDiv.innerHTML = '';
    cards = data.card_on_table;
    if(cards) {
        cards.forEach((card, index) => {
            const cardElement = document.createElement('div');
            cardElement.className = 'card';
            cardElement.id = `card-${index}`;
            cardElement.textContent = `${card.value} de ${getSuitName(card.color)}`;
            cardTableDiv.appendChild(cardElement);
        });
    }
});

socket.on('start_game_error', (data) => {
    alert(`Erreur : ${data.message}`);
});