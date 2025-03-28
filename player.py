from flask_socketio import emit

class Player:
    def __init__(self, name, team, sid):
        self.name = name
        self.team = team
        self.sid = sid
        self.cards = []

    def dump(self):
         return {"name": self.name, "team": self.team, "sid": self.sid}

    def sendDeck(self):
        self.emit("update_deck", self.cards)

    def emit(self, type, data):
        if self.sid != None:
            emit(type, data, room=self.sid)

    def __repr__(self):
        return str(self.dump())