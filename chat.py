from flask_socketio import emit
import time

class Chat:
    def __init__(self, gManager, logManager, attachedgameID):
        self.attachedGameManager = gManager
        self.attachedLogManager = logManager
        self.attachedGameID = attachedgameID
        self.messages = []
        self.cachedMessage = []

    def registerChat(self, player, message):
        self.logMessage(player, message["message"])
        self.broadcastMessage(player, message["message"])
        self.cachedMessage.append((player, {"message": message["message"]}))
        if len(self.cachedMessage) > 8:
            self.cachedMessage = self.cachedMessage[1:]

    def registerGif(self, player, gif_url):
        current_time = time.strftime("%H:%M", time.localtime())
        self.logMessage(player, f"GIF: {gif_url}")
        emit("receive_chat_gif", {"gif_url": gif_url, "player": player.name, "time": current_time}, broadcast=True)
        self.cachedMessage.append((player, {"gif_url": gif_url}))
        if len(self.cachedMessage) > 8:
            self.cachedMessage = self.cachedMessage[1:]

    def resumeChat(self, player):
        for p, msg in self.cachedMessage:
            current_time = time.strftime("%H:%M", time.localtime())
            if "gif_url" in msg:
                emit("receive_chat_gif", {"gif_url": msg["gif_url"], "player": p.name, "time": current_time}, room=player.sid)
            else:
                emit("receive_chat_message", {"message": msg["message"], "player": p.name, "time": current_time}, room=player.sid)

    def broadcastMessage(self, player, message):
        current_time = time.strftime("%H:%M", time.localtime())
        emit("receive_chat_message", {"message": message, "player": player.name, "time": current_time}, broadcast=True)
        emit("launch-toast", {"message": f"{player.name} - {message}", "category": "success"}, broadcast=True)

    def logMessage(self, player, message):
        self.attachedLogManager.logChat({"message": message, "player": player.dump()})