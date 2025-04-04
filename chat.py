from flask_socketio import emit
import time

class Chat:
    def __init__(self, gManager, logManager, attachedgameID):
        self.attachedGameManager = gManager
        self.attachedLogManager = logManager
        self.attachedGameID = attachedgameID
        self.messages = []

    def registerChat(self, player, message):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logMessage(player, message["message"])
        self.broadcastMessage(player,  message["message"])

    def broadcastMessage(self, player, message):
        current_time = time.strftime("%H:%M", time.localtime())
        emit("receive_chat_message", {"message": message, "player": player.name, "time": current_time}, broadcast=True)

    def logMessage(self, player, message):
        self.attachedLogManager.logChat({"message": message, "player": player.dump()})