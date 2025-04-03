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
    <div class="row justify-content-center">
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

// Request initial games update
socket.emit('request_games_update');

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

