import { getRoundStatusText, getSuitName, getFormattedTalk, getCardElement } from "../utils.js"
import { ROUND_STATE_SETUP, ROUND_STATE_TALKING, ROUND_STATE_PLAYING } from "../utils.js";

const roundInfoDiv = document.getElementById('roundInfo');
const cardTableDiv = document.getElementById('cardTable');
const talkInfoDiv = document.getElementById("talkInfo");
const talkInfoConfirmBtn = document.getElementById('confirmBtn');

const talkInfoPassBtn = document.getElementById('passBtn');
const talkInfoContrerBtn = document.getElementById('contrerBtn');
const talkInfoSurContrerBtn = document.getElementById('surContreeBtn');


socket.on('round_info', (data) => {
    console.log("round_info: ", data)
    const roundState = data.state;
    if(roundState == ROUND_STATE_TALKING) {
        roundInfoDiv.innerHTML = `
            <p>Statut de la manche : ${getRoundStatusText(data.state)}</p>
            <p>Prochain à parler : ${data.next_talk}</p>
            <p>Contrat : ${("current_talk" in data ? getFormattedTalk(data) : "")}</p>
        `;
        talkInfoDiv.style.display = 'flex';
    }
    else if(roundState == ROUND_STATE_PLAYING) {
        roundInfoDiv.innerHTML = `
            <p>Statut de la manche : ${getRoundStatusText(data.state)}</p>
            <p>Prochain à jouer : ${data.next_turn}</p>
            <p>Contrat : ${("current_talk" in data ? getFormattedTalk(data) : "")}</p>
            <p>Plis: ${data.trick[0]} - ${data.trick[1]}</p>
        `;
        talkInfoDiv.style.display = 'none';
        // -------------------------------------------------------
        // INTERACT ON TABLE CARD
        if("card_on_table" in data) {
            cardTableDiv.innerHTML = '';
            const cards = data.card_on_table;
            cards.forEach((card, index) => {
                    const cardElement = getCardElement(card.card, index);
                    cardTableDiv.appendChild(cardElement);

                    cardElement.addEventListener('click', () => {
                        socket.emit('card_clicked', {"card_id": cardElement.id});
                    });
            });
        }
    }
});

cardTableDiv.addEventListener('click', function() {
    socket.emit('table_ack_click');
});

talkInfoConfirmBtn.addEventListener('click', function() {
    const selectedColor = document.getElementById('colorSelect').value;
    const selectedValue = document.getElementById('pointSelect').value;
    socket.emit('talk_click', {selectedColor, selectedValue});
});

talkInfoPassBtn.addEventListener('click', function() {
    socket.emit('pass_click');
});

talkInfoContrerBtn.addEventListener('click', function() {
    socket.emit('contrer_click');
});

talkInfoSurContrerBtn.addEventListener('click', function() {
    socket.emit('sur_contrer_click');
});

socket.on('start_game_error', (data) => {
    alert(`Erreur : ${data.message}`);
});