window.socket = io({
    withCredentials: true
});
socket.emit('request_game_info');

const teamSelect = document.getElementById('team');
const joinBtn = document.getElementById('joinBtn');

socket.on('connect', () => {
    console.log('Connecté au serveur');
});

// Gestionnaire pour rejoindre une partie
joinBtn.addEventListener('click', () => {
    const team = parseInt(teamSelect.value);

    socket.emit('join_game', { team });
});
