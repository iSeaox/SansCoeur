window.socket = io({
  withCredentials: true
});

const params = new URLSearchParams(window.location.search);
const data = Object.fromEntries(params.entries());
socket.emit('connect_game', data);
socket.emit('request_game_info');

document.addEventListener('DOMContentLoaded', () => {
  const usernameSpan = document.getElementById('username');
  const username = usernameSpan.textContent;

  const capitalizedUsername =
    username.charAt(0).toUpperCase() + username.slice(1);
  usernameSpan.textContent = capitalizedUsername;
});

socket.on('end_game', (data) => {
  if (data.redirect) {
      window.location.href = data.redirect;
  }
});


