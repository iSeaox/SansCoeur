import { sendToast } from "./utils.js";

socket.on("launch-toast", ({ message, category }) => {
    console.log(message, category)
    sendToast(message, category);
});