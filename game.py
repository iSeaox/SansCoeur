import player
import round

import random

from flask_socketio import emit

GAME_STATUS_WAITING = 0
GAME_STATUS_PLAYING = 1
GAME_STATUS_END = 2
# _____________________________________________________
CARD_COLOR_SPADES = 0
CARD_COLOR_HEARTS = 1
CARD_COLOR_DIAMONDS = 2
CARD_COLOR_CLUBS = 3
# _____________________________________________________
CARD_VALUE_7 = 7
CARD_VALUE_8 = 8
CARD_VALUE_9 = 9
CARD_VALUE_10 = 10
CARD_VALUE_JACK = 11
CARD_VALUE_QUEEN = 12
CARD_VALUE_KING = 13
CARD_VALUE_ACE = 14
# _____________________________________________________
class Game:
    def __init__(self):
        self._cards = []
        self._players = []
        self._status = GAME_STATUS_WAITING
        self._readyToStart = False
        self._currentRound = None

    def setupDeck(self):
        colors = [CARD_COLOR_SPADES, CARD_COLOR_HEARTS, CARD_COLOR_DIAMONDS, CARD_COLOR_CLUBS]

        values = [
            CARD_VALUE_7, CARD_VALUE_8, CARD_VALUE_9, CARD_VALUE_10,
            CARD_VALUE_JACK, CARD_VALUE_QUEEN, CARD_VALUE_KING, CARD_VALUE_ACE
        ]

        for color in colors:
            for value in values:
                self._cards.append({"color": color, "value": value})
        random.shuffle(self._cards)


    def registerPlayer(self, name, team, sid):
        for p in self._players:
            if p.name == name:
                return (False, "Already connected")
        if(len(self.getTeam(team)) == 2):
            return (False, f"Team {team} is full")

        self._players.append(player.Player(name, team, sid))
        if len(self._players) == 4:
            self._readyToStart = True
        return (True, "Success")

    def resumePlayer(self, name, sid):
        player = self.getPlayerByName(name)
        player.sid = sid
        if player != None:
            self.broadcastGameInfo()
            self.getCurrentRound().sendRoundInfo()
            player.sendDeck()

    def getTeam(self, team):
        out = []
        for pl in self._players:
            if pl.team == team:
                out.append(pl)
        return out

    def getPlayerByName(self, name):
        for p in self._players:
            if p.name == name:
                return p
        return None

    def dumpPlayers(self):
        out = []
        print(self._players)
        for p in self._players:
            out.append(p.dump())
        return out

    def dumpGameInfo(self):
        return {
            "players": self.dumpPlayers(),
            "status": self._status,
            "readyToStart": self._readyToStart
        }

    def broadcastGameInfo(self):
        emit('game_info', self.dumpGameInfo(), broadcast=True)

    def start(self):
        # _____________________________________________________
        # Intial Check
        if(self._status == GAME_STATUS_PLAYING):
            return (False, "Already started")

        if(len(self._players) < 4):
            return (False, "Not enough players")

        team0 = self.getTeam(0)
        team1 = self.getTeam(1)
        if len(team0) != 2 or len(team1) != 2:
            return (False, "Team error")
        # _____________________________________________________
        # Setup
        team0 = self.getTeam(0)
        team1 = self.getTeam(1)
        self._players = [team0[0], team1[0], team0[1], team1[1]]
        # TODO : DEBUG la ligne du dessous sert à debug
        self._players.reverse()

        self._status = GAME_STATUS_PLAYING

        self.setupDeck()
        self._currentRound = round.Round(self._players, 0, self._cards)
        self._currentRound.start()
        self.broadcastGameInfo()
        return (True, "Starting game")

        # _____________________________________________________

    def getCurrentRound(self):
        return self._currentRound