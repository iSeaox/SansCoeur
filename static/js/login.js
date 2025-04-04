import { sendToast } from "./utils.js";

document.addEventListener("DOMContentLoaded", function () {
  const titleElement = document.querySelector(".title");
  const text = titleElement.textContent;
  titleElement.innerHTML = "";
  for (let i = 0; i < text.length; i++) {
    const span = document.createElement("span");
    span.textContent = text[i] === " " ? "\u00A0" : text[i];
    span.style.setProperty("--i", i);
    titleElement.appendChild(span);
  }

  const forgotLink = document.querySelector(".login-forgot");
  forgotLink.addEventListener("click", function (e) {
    e.preventDefault();

    sendToast("CHEHHHHH", "info");
  });
});
