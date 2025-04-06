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
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logMessage(player, message["message"])
        self.broadcastMessage(player,  message["message"])
        self.cachedMessage.append((player, message["message"]))
        if len(self.cachedMessage) > 8:
            self.cachedMessage = self.cachedMessage[1:]

    def resumeChat(self, player):
        for p, msg in self.cachedMessage:
            current_time = time.strftime("%H:%M", time.localtime())
            emit("receive_chat_message", {"message": msg, "player": p.name, "time": current_time}, room=player.sid)

    def broadcastMessage(self, player, message):
        current_time = time.strftime("%H:%M", time.localtime())
        emit("receive_chat_message", {"message": message, "player": player.name, "time": current_time}, broadcast=True)
        emit('launch-toast', {'message': f"{player.name} - {message}", "category": "success"}, broadcast=True)

    def logMessage(self, player, message):
        self.attachedLogManager.logChat({"message": message, "player": player.dump()})