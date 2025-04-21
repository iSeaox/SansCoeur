import player
import roundManager

import random

from flask import url_for, current_app
import uuid
import chat

import logging
logger = logging.getLogger(f"app.{__name__}")

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
    def __init__(self, gameManager, logManager):
        self.gameManager = gameManager
        self.logManager = logManager
        self.maxPoints = 0
        self._cards = []
        self._players = []
        self._status = GAME_STATUS_WAITING
        self._readyToStart = False
        self.roundManager = roundManager.RoundManager()
        self.nbRound = 0
        self.score = [0, 0]
        self.roundScore = []
        self.id = int(str(uuid.uuid4().int)[:8])
        self.chat = chat.Chat(self.gameManager, self.logManager, self.id)

    def setupDeck(self):
        # TODO : gérer la distribution des cartes mieux que ça
        self._cards = []
        colors = [CARD_COLOR_SPADES, CARD_COLOR_HEARTS, CARD_COLOR_DIAMONDS, CARD_COLOR_CLUBS]

        values = [
            CARD_VALUE_7, CARD_VALUE_8, CARD_VALUE_9, CARD_VALUE_10,
            CARD_VALUE_JACK, CARD_VALUE_QUEEN, CARD_VALUE_KING, CARD_VALUE_ACE
        ]

        for color in colors:
            for value in values:
                self._cards.append({"color": color, "value": value})
        random.shuffle(self._cards)

    def removePlayer(self, name):
        if self._status == GAME_STATUS_WAITING:
            player = self.getPlayerByName(name)
            if player:
                self._players.remove(player)
                self._readyToStart = False
                self.broadcastGameInfo()
                return (True, f"Game sucessfully quit")
        elif self._status == GAME_STATUS_END:
            player = self.getPlayerByName(name)
            if player:
                self._players.remove(player)
                self.broadcastGameInfo()

                if len(self._players) == 0:
                    self.gameManager.roomManager.broadcast_to_room(
                        f"game-{self.id}", 'end_game',
                        {"redirect": url_for('index')}
                    )

                    self.gameManager.deleteGame(self)

                return (True, f"Game sucessfully quit")
        else:
            return (False, f"You can't quit a started game")

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
            self.chat.resumeChat(player)
            self.broadcastGameInfo()
            if self.getCurrentRound() != None:
                self.getCurrentRound().sendRoundInfo()
                player.sendDeck()
            return True
        return False

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
        for p in self._players:
            out.append(p.dump())
        return out

    def dumpGameInfo(self):
        out = {
            "id": self.id,
            "players": self.dumpPlayers(),
            "status": self._status,
            "readyToStart": self._readyToStart,
            "score": self.score,
            "round_score": self.roundScore
        }

        if self._status == GAME_STATUS_WAITING:
            lastGameData = self.logManager.getLastGameData()
            if lastGameData:
                out.update({
                    "last_game_data": {
                        "players": lastGameData["players"],
                        "score": lastGameData["score"]
                    }
                })
        return out

    def broadcastGameInfo(self):
        self.gameManager.roomManager.broadcast_to_room(
            f"game-{self.id}", "game_info", self.dumpGameInfo(), skip_sid=None
        )

    def startNewRound(self):
        self.setupDeck()
        # Pour eviter les doublons lors du restart
        self.roundManager.deleteRound(self.getCurrentRound())
        self.roundManager.registerNewRound(self.id, self._players, self.nbRound % 4, self._cards, self.gameManager)
        self.getCurrentRound().start()
        self.getCurrentRound().sendRoundInfo()
        self.broadcastGameInfo()

    def start(self, maxPoints):
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
        self.maxPoints = maxPoints
        team0 = self.getTeam(0)
        team1 = self.getTeam(1)
        self._players = [team0[0], team1[0], team0[1], team1[1]]

        self._status = GAME_STATUS_PLAYING

        # _____________________________________________________
        # DEBUG
        if current_app.config["DEBUG_MODE_FAKE_ROUNDS"]:
            for i in range(0, 8):
                sTeam0 = random.randint(0, 160)
                self.roundScore.append({
                    "score": [sTeam0, 162 - sTeam0],
                    "talk": {
                        "value": random.randint(80, 162),
                        "team": random.randint(0, 1)
                    }
                })
        # _____________________________________________________
        self.startNewRound()
        return (True, "Starting game")

    def end(self):
        self._status = GAME_STATUS_END
        self.gameManager.roomManager.broadcast_to_room(
            f"game-{self.id}", 'launch-toast',
            {'message': "La partie est terminée", "category": "success"}
        )

        self.broadcastGameInfo()
        self.logManager.logGame(self)
        self.gameManager.registerNewGame()

    def registerScore(self, score, belote=-1):
        currentTalk = self.getCurrentRound().talk
        talkTeam = currentTalk["player"].team

        logger.debug(
            f"\n{'-' * 60}\n"
            f"Belote: {belote}\n"
            f"Talk: \n\tColor: {currentTalk['color']}\n\tValue: {currentTalk['value']}\n\tTeam: {currentTalk['player'].team}\n"
            f"\tContrer: {self.getCurrentRound().contrer}\n"
            f"\tSur-contrer: {self.getCurrentRound().surcontrer}\n"
            f"Score: \n\tTeam {self.getTeam(0)[0].name} - {self.getTeam(0)[1].name} (0): {score[0]} {"+ 20" if belote == 0 else ""}\n"
            f"\tTeam {self.getTeam(1)[0].name} - {self.getTeam(1)[1].name} (1): {score[1]} {"+ 20" if belote == 1 else ""}\n"
            f"\tTotal: {score[0] + score[1]}\n"
            f"{'-' * 60}"
        )

        if belote == talkTeam:
            score[belote] += 20

        multi = (2 if "contrer" in currentTalk else 1)
        multi *= (2 if "surcontrer" in currentTalk else 1)

        if currentTalk["value"] == 162 or currentTalk["value"] == 182:
            if currentTalk["value"] == score[talkTeam]:
                self.score[talkTeam] += (320 + score[talkTeam]) * multi
            else:
                self.score[not(talkTeam)] += ((320 + 162) // 10 * 10) * multi

        if currentTalk["value"] <= score[talkTeam] and score[talkTeam] > 80:
            self.score[talkTeam] += ((currentTalk["value"] + score[talkTeam]) // 10 * 10) * multi
            self.score[not(talkTeam)] += (score[not(talkTeam)]) // 10 * 10
        else:
            self.score[not(talkTeam)] += ((162 + currentTalk["value"]) // 10 * 10) * multi

        self.nbRound += 1
        if belote != talkTeam:
            self.score[belote] += 20


        # Mise à jour du tableau des scores
        self.roundScore.append({
            "score": [score[0], score[1]],
            "talk": {
                "value": currentTalk["value"],
                "team": talkTeam
            }
        })

        # Verifier si la game est finie
        if self.score[0] >= self.maxPoints or self.score[1] > self.maxPoints:
            self.end()
            return
        self.startNewRound()

    def getCurrentRound(self):
        return self.roundManager.getRound()