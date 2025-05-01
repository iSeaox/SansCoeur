import { sendToast } from "./utils.js";

window.info_socket = io("/info",{
    withCredentials: true
});

info_socket.on("launch-toast", ({ message, category }) => {
    console.log(message, category)
    sendToast(message, category);
});

// For in game toasts
socket.on("launch-toast", ({ message, category }) => {
    console.log(message, category)
    sendToast(message, category);
});