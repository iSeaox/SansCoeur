window.socket = io({
  withCredentials: true
});

window.admin_socket = io("/admin", {
  withCredentials: true
});

document.addEventListener("DOMContentLoaded", function () {
    // Animation du titre comme sur la page de login
    const titleElement = document.querySelector(".title");
    const text = titleElement.textContent;
    titleElement.innerHTML = "";
    for (let i = 0; i < text.length; i++) {
      const span = document.createElement("span");
      span.textContent = text[i] === " " ? "\u00A0" : text[i];
      span.style.setProperty("--i", i);
      titleElement.appendChild(span);
    }
  });