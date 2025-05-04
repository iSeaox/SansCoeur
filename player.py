from flask_socketio import emit
from round import getBeloteValue

class Player:
    def __init__(self, name, team, sid, spec=False):
        self.name = name
        self.spec = spec
        self.team = team
        self.sid = sid
        self.cards = []
        self.cardReactionTime = []

    def dump(self):
         return {"name": self.name, "team": self.team, "sid": self.sid, "reaction_time": self.cardReactionTime}

    def sendDeck(self):
        self.emit("update_deck", self.cards)

    def emit(self, type, data):
        if self.sid != None:
            emit(type, data, room=self.sid)

    def hasColor(self, color):
        for c in self.cards:
            if c["color"] == color:
                return True
        return False

    def hasUpper(self, card, trump):
        for c in self.cards:
            if c["color"] == card['color']:
                if getBeloteValue(c, trump) > getBeloteValue(card, trump):
                    return True, c
        return False, {}

    def __repr__(self):
        return str(self.dump())