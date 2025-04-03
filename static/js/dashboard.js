window.socket = io({
  withCredentials: true
});
socket.emit('request_game_info');

document.addEventListener('DOMContentLoaded', () => {
  const usernameSpan = document.getElementById('username');
  const username = usernameSpan.textContent;

  const capitalizedUsername =
    username.charAt(0).toUpperCase() + username.slice(1);
  usernameSpan.textContent = capitalizedUsername;
});
