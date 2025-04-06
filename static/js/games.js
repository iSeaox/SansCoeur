window.socket = io({
    withCredentials: true
});

function createGameCard(game) {
    const gameId = game.id || "Unknown ID";
    const playersCount = game.players ? game.players.length : 0;
    const maxPlayers = 4;
    const statusColor = game.status === 1 ? "red" : "green";
    const statusText = game.status === 1 ? "En cours" : "En attente";

    const team0Players = game.players.filter(player => player.team === 0);
    const team1Players = game.players.filter(player => player.team === 1);

    const cardHTML = `
    <div class="row justify-content-center mb-5">
        <div class="card col-md-8">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-4">
                        <h5>ID: ${gameId}</h5>
                    </div>
                    <div class="col-4">
                        <h5>${playersCount}/${maxPlayers} joueurs</h5>
                    </div>
                    <div class="col-4">
                        <span class="status-indicator" style="background-color: ${statusColor}; width: 15px; height: 15px; border-radius: 50%; display: inline-block;"></span>
                        <span>${statusText}</span>
                    </div>
                </div>
                <div class="row align-items-center mt-3">
                    <div class="col-6 d-flex align-items-center justify-content-center">
                        <h6>Équipe 0: ${team0Players.map(player => player.name).join(' - ')} ${team0Players.length < 2 ? `<button class="btn btn-primary ms-2" id="join-game-${gameId}-0">Rejoindre</button>` : ''}</h6>
                    </div>
                    <div class="col-6 d-flex align-items-center justify-content-center">
                        <h6>Équipe 1: ${team1Players.map(player => player.name).join(' - ')} ${team1Players.length < 2 ? `<button class="btn btn-primary ms-2" id="join-game-${gameId}-1">Rejoindre</button>` : ''}</h6>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `;

    // Add event listener to the button after the card is rendered
    setTimeout(() => {
        const button = document.getElementById(`join-game-${gameId}-0`);
        if (button) {
            button.addEventListener('click', () => {
                socket.emit("join_game", {"id": gameId, "team": 0});
            });
        }
    }, 0);

    setTimeout(() => {
        const button = document.getElementById(`join-game-${gameId}-1`);
        if (button) {
            button.addEventListener('click', () => {
                socket.emit("join_game", {"id": gameId, "team": 1});
            });
        }
    }, 0);

    return cardHTML;
}
const gameListDiv = document.getElementById("games-list");
const lastGameDiv = document.getElementById("last-game");

// Request initial games update
socket.emit('request_games_update');
socket.emit('request_last_game_data');

socket.on('last_game_data_update', (data) => {
    console.log(data)
    lastGameDiv.innerHTML = "";

    const team0Players = data.players.filter(player => player.team === 0).map(player => player.name).join(' - ');
    const team1Players = data.players.filter(player => player.team === 1).map(player => player.name).join(' - ');

    const nbRound = data.round_score.length;

    const lastGameHTML = `
        <div class="row align-items-center">
            <div class="col-6">
                <h5>${team0Players}</h5>
                <h6>${data.score[0]}</h6>
            </div>
            <div class="col-6">
                <h5>${team1Players}</h5>
                <h6>${data.score[1]}</h6>
            </div>
        </div>
        <div class="row align-items-center mt-3">
            <div class="col-12">
                <h5>Manche décisive:</h5>
                <p>${data.round_score[nbRound - 1].score[0]} - ${data.round_score[nbRound - 1].score[1]}</p>
                <p>(Contrat: ${data.round_score[nbRound - 1].talk.value} points, Équipe ${data.round_score[nbRound - 1].talk.team})</p>
            </div>
        </div>
        <div class="row justify-content-end mt-3">
            <p class="text-start" style="color: #505050">ID: ${data.id} - ${data.time ? data.time : "Time not available"}</p>
        </div>
    `;

    lastGameDiv.innerHTML = lastGameHTML;
});

// Listen for updates and refresh the games list
socket.on('update_games', (data) => {
    gameListDiv.innerHTML = `
    <div class="row justify-content-center">
        <div class="col-md-10">`;

    data.games.forEach(game => {
        gameListDiv.innerHTML += createGameCard(game);
    });

    gameListDiv.innerHTML += `
        </div>
    </div>`;
});

// Listen for join_success event and handle redirection
socket.on('join_success', (data) => {
    if (data.redirect) {
        window.location.href = data.redirect;
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const usernameSpan = document.getElementById('username');
    const username = usernameSpan.textContent;

    const capitalizedUsername =
      username.charAt(0).toUpperCase() + username.slice(1);
    usernameSpan.textContent = capitalizedUsername;
  });

