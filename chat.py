from flask_socketio import emit
import time
import player

class Chat:
    def __init__(self, gManager, logManager, attachedgameID):
        self.attachedGameManager = gManager
        self.attachedLogManager = logManager
        self.attachedGameID = attachedgameID
        self.messages = []
        self.cachedMessage = []

    def _emitBroadcast(self, event, data):
        self.attachedGameManager.roomManager.broadcast_to_room(
            f"game-{self.attachedGameID}", event, data, skip_sid=None
        )

    def registerSpecChat(self, player_name, sid, message):
        fake_player = player.Player(player_name, -1, sid, spec=True)
        self.registerChat(fake_player, message)

    def registerSpecGif(self, player_name, sid, gif_url):
        fake_player = player.Player(player_name, -1, sid, spec=True)
        self.registerGif(fake_player, gif_url)

    def registerChat(self, player, message):
        self.logMessage(player, message["message"])
        self.broadcastMessage(player, message["message"])
        self.cachedMessage.append((player, {"message": message["message"]}))
        if len(self.cachedMessage) > 8:
            self.cachedMessage = self.cachedMessage[1:]

    def registerGif(self, player, gif_url):
        current_time = time.strftime("%H:%M", time.localtime())
        self.logMessage(player, f"GIF: {gif_url}")
        if player.spec:
            self._emitBroadcast("receive_chat_gif", {"gif_url": gif_url, "player": player.name, "time": current_time, "spec": True})
        else:
            self._emitBroadcast("receive_chat_gif", {"gif_url": gif_url, "player": player.name, "time": current_time})
        self.cachedMessage.append((player, {"gif_url": gif_url}))
        if len(self.cachedMessage) > 8:
            self.cachedMessage = self.cachedMessage[1:]

    def resumeChat(self, player):
        for p, msg in self.cachedMessage:
            current_time = time.strftime("%H:%M", time.localtime())
            event = ""
            data = {}
            if "gif_url" in msg:
                event = "receive_chat_gif"
                data = {"gif_url": msg["gif_url"], "player": p.name, "time": current_time}
                emit("receive_chat_gif", {"gif_url": msg["gif_url"], "player": p.name, "time": current_time}, room=player.sid)
            else:
                event = "receive_chat_message"
                data = {"message": msg["message"], "player": p.name, "time": current_time}

            if p.spec:
                data["spec"] = True

            emit(event, data, room=player.sid)
    def broadcastMessage(self, player, message):
        current_time = time.strftime("%H:%M", time.localtime())

        if player.spec:
            self._emitBroadcast("receive_chat_message", {"message": message, "player": player.name, "spec": True, "time": current_time})
            self._emitBroadcast("launch-toast", {"message": f"{player.name} - {message}", "category": "secondary"})
        else:
            self._emitBroadcast("receive_chat_message", {"message": message, "player": player.name, "time": current_time})
            self._emitBroadcast("launch-toast", {"message": f"{player.name} - {message}", "category": "success"})

    def logMessage(self, player, message):
        self.attachedLogManager.logChat({"message": message, "player": player.dump()})