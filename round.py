from flask_socketio import emit
from flask import current_app
import time
import logging
import random
logger = logging.getLogger(f"app.{__name__}")

ROUND_STATE_SETUP = 0
ROUND_STATE_TALKING = 1
ROUND_STATE_PLAYING = 2

TRUMP_CONVERT_TABLE   = {7: 15, 8: 16, 12: 17, 13: 18, 10: 19, 14: 20, 9: 21, 11: 22}
CLASSIC_CONVERT_TABLE = {7: 7, 8: 8, 9: 9, 11: 10, 12: 11, 13: 12, 10: 13, 14: 14}

TRUMP_POINT_TABLE   = {7: 0, 8: 0, 9: 14, 10: 10, 11: 20, 12: 3, 13: 4, 14: 11}
CLASSIC_POINT_TABLE = {7: 0, 8: 0, 9: 0 , 10: 10, 11: 2 , 12: 3, 13: 4, 14: 11}

TALBE_ACK_COOLDOWN_NS = (10 ** 9) * 1

def getBeloteValue(card, trump):
    return (TRUMP_CONVERT_TABLE if card["color"] == trump else CLASSIC_CONVERT_TABLE)[card["value"]]

def getBelotePoint(card, trump):
    return (TRUMP_POINT_TABLE if card["color"] == trump else CLASSIC_POINT_TABLE)[card["value"]]
class Round:

    def __init__(self, players, firstDistribIndex, cards, gManager, attachedGameID):
        self.attachedGameID = attachedGameID
        self.attachedGameManger = gManager
        self.players = players
        self.firstDistribIndex = firstDistribIndex
        self.firstDistribIndex %= 4
        self.cards = cards
        self.state = ROUND_STATE_SETUP
        self.nextTurnIndex = self.firstDistribIndex + 1
        self.nextTurnIndex %= 4
        self.nextTurn = self.players[self.nextTurnIndex]

        self.nextTalkIndex = self.firstDistribIndex + 1
        self.nextTalkIndex %= 4
        self.nextTalk = self.players[self.nextTalkIndex]
        self.talk = {}
        self.lastTalk = []
        self.contrer = 0
        self.surcontrer = 0
        self.belote = -1 # Team si il y a une belote

        self.needTableAck = 0 # ACK to remove cards from the table
        self.tableAckTime = 0
        self.cardReactionTimeBegin = 0

        # Hand variable
        self.cardOnTable = []
        self.winningTeam = None # Savoir qui a la main
        self.winningPlayer = None
        self.askedColor = None
        self.winningCard = None

        self.heapTeam = [[], []]

    def _emitBroadcast(self, event, data):
        self.attachedGameManger.roomManager.broadcast_to_room(
            f"game-{self.attachedGameID}", event, data, skip_sid=None
        )

    def dumpRoundInfo(self):
        out = {
            "state": self.state,
        }

        if self.talk != {}:
            out.update({"current_talk": {
                    "color": self.talk['color'],
                    "value": self.talk['value'],
                    "player": self.talk['player'].name
                }})

        if len(self.lastTalk) > 0:
            out["last_talk"] = []

        for lTalk in self.lastTalk:
            out["last_talk"].append({
                    "color": lTalk['color'],
                    "value": lTalk['value'],
                    "player": lTalk['player'].name
                })

        higherTalkTeam0 = {}
        higherTalkTeam1 = {}

        temp_talks = self.lastTalk.copy()
        if(self.talk != {}):
            temp_talks.append(self.talk)
        for t in temp_talks:
            if t['player'].team == 0:
                if higherTalkTeam0 == {}:
                    higherTalkTeam0 = t
                elif t['value'] > higherTalkTeam0['value']:
                    higherTalkTeam0 = t

            elif t["player"].team == 1:
                if higherTalkTeam1 == {}:
                    higherTalkTeam1 = t
                elif t['value'] > higherTalkTeam1['value']:
                    higherTalkTeam1 = t

        if higherTalkTeam0 != {}:
            out["higher_talk_0"] = {
                    "color": higherTalkTeam0['color'],
                    "value": higherTalkTeam0['value'],
                    "player": higherTalkTeam0['player'].name
                }

        if higherTalkTeam1 != {}:
            out["higher_talk_1"] = {
                    "color": higherTalkTeam1['color'],
                    "value": higherTalkTeam1['value'],
                    "player": higherTalkTeam1['player'].name
                }

        if self.contrer:
            out.update({
                "contrer": {
                    "player": self.talk['contrer'].name,
                    "team": self.talk['contrer'].team,
                }
            })

        if self.surcontrer:
            out.update({
                "surcontrer": {
                    "player": self.talk['surcontrer'].name,
                    "team": self.talk['surcontrer'].team,
                }
            })

        if self.state == ROUND_STATE_TALKING:
            out.update({
                "next_talk": self.nextTalk.name,
            })
        elif self.state == ROUND_STATE_PLAYING:
            out.update({
                "next_turn": self.nextTurn.name,
                "card_on_table": [],
                "trick": [len(self.heapTeam[0]), len(self.heapTeam[1])]
            })
            for c in self.cardOnTable:
                out["card_on_table"].append({"card": c["card"], "player": c["player"].name})
        else:
            pass
        return out

    def sendRoundInfo(self):
        self._emitBroadcast('round_info', self.dumpRoundInfo())

    def cardsDistrib(self):
        # Distribution des cartes
        schem = [3, 2, 3]
        for nbCard in schem:
            for p in self.players:
                for i in range(nbCard):
                    p.cards.append(self.cards.pop())

        # Notifier les joueurs
        for p in self.players:
            p.sendDeck()

        self.state = ROUND_STATE_TALKING
        self.sendRoundInfo()

    def start(self):
        self.cardsDistrib()
        if self.firstDistribIndex == 0:

            if current_app.config["DEBUG_MODE_TALKS"]:

                self.state = ROUND_STATE_PLAYING
                self.talk =  {"color": 2, "value": 100, "player": self.players[0]}
                self.cardReactionTimeBegin = time.time()

                for p in self.players:
                    p.cards = sorted(p.cards, key=lambda x: (x["color"], getBeloteValue(x, self.talk["color"])), reverse=True)
                    p.sendDeck()

            if current_app.config["DEBUG_MODE_TABLE_CARDS"]:
                for p in self.players:
                    self.cardOnTable.append({"card": p.cards.pop(), "player": p})

            if current_app.config["DEBUG_MODE_END_GAME"]:
                logger.debug("END GAME")
                self.winningTeam = 0
                self.needTableAck = 1
                self.heapTeam = [[[{'card': {'color': 3, 'value': 9}, 'player': {'name': 'guillaume', 'team': 1, 'sid': 'qdwderwekmSIvEBaAAAB'}}, {'card': {'color': 3, 'value': 10}, 'player': {'name': 'mathias', 'team': 0, 'sid': '1j5fKRlJ9RyKONgJAAAD'}}, {'card': {'color': 3, 'value': 7}, 'player': {'name': 'helios', 'team': 1, 'sid': 'J1RTyB8TaKd9NxSmAAAF'}}, {'card': {'color': 1, 'value': 12}, 'player': {'name': 'magathe', 'team': 0, 'sid': 'bxRbaqkv4dguxVOVAAAH'}}], [{'card': {'color': 0, 'value': 14}, 'player': {'name': 'mathias', 'team': 0, 'sid': '1j5fKRlJ9RyKONgJAAAD'}}, {'card': {'color': 0, 'value': 9}, 'player': {'name': 'helios', 'team': 1, 'sid': 'J1RTyB8TaKd9NxSmAAAF'}}, {'card': {'color': 0, 'value': 13}, 'player': {'name': 'magathe', 'team': 0, 'sid': 'bxRbaqkv4dguxVOVAAAH'}}, {'card': {'color': 0, 'value': 8}, 'player': {'name': 'guillaume', 'team': 1, 'sid': 'qdwderwekmSIvEBaAAAB'}}], [{'card': {'color': 2, 'value': 14}, 'player': {'name': 'mathias', 'team': 0, 'sid': '1j5fKRlJ9RyKONgJAAAD'}}, {'card': {'color': 2, 'value': 9}, 'player': {'name': 'helios', 'team': 1, 'sid': 'J1RTyB8TaKd9NxSmAAAF'}}, {'card': {'color': 2, 'value': 11}, 'player': {'name': 'magathe', 'team': 0, 'sid': 'bxRbaqkv4dguxVOVAAAH'}}, {'card': {'color': 2, 'value': 10}, 'player': {'name': 'guillaume', 'team': 1, 'sid': 'qdwderwekmSIvEBaAAAB'}}], [{'card': {'color': 0, 'value': 11}, 'player': {'name': 'helios', 'team': 1, 'sid': 'J1RTyB8TaKd9NxSmAAAF'}}, {'card': {'color': 2, 'value': 8}, 'player': {'name': 'magathe', 'team': 0, 'sid': 'bxRbaqkv4dguxVOVAAAH'}}, {'card': {'color': 3, 'value': 13}, 'player': {'name': 'guillaume', 'team': 1, 'sid': 'qdwderwekmSIvEBaAAAB'}}, {'card': {'color': 2, 'value': 12}, 'player': {'name': 'mathias', 'team': 0, 'sid': '1j5fKRlJ9RyKONgJAAAD'}}], [{'card': {'color': 2, 'value': 13}, 'player': {'name': 'mathias', 'team': 0, 'sid': '1j5fKRlJ9RyKONgJAAAD'}}, {'card': {'color': 1, 'value': 7}, 'player': {'name': 'helios', 'team': 1, 'sid': 'J1RTyB8TaKd9NxSmAAAF'}}, {'card': {'color': 2, 'value': 7}, 'player': {'name': 'magathe', 'team': 0, 'sid': 'bxRbaqkv4dguxVOVAAAH'}}, {'card': {'color': 1, 'value': 10}, 'player': {'name': 'guillaume', 'team': 1, 'sid': 'qdwderwekmSIvEBaAAAB'}}]], [[{'card': {'color': 1, 'value': 14}, 'player': {'name': 'guillaume', 'team': 1, 'sid': 'qdwderwekmSIvEBaAAAB'}}, {'card': {'color': 1, 'value': 11}, 'player': {'name': 'mathias', 'team': 0, 'sid': '1j5fKRlJ9RyKONgJAAAD'}}, {'card': {'color': 1, 'value': 13}, 'player': {'name': 'helios', 'team': 1, 'sid': 'J1RTyB8TaKd9NxSmAAAF'}}, {'card': {'color': 1, 'value': 8}, 'player': {'name': 'magathe', 'team': 0, 'sid': 'bxRbaqkv4dguxVOVAAAH'}}], [{'card': {'color': 3, 'value': 14}, 'player': {'name': 'guillaume', 'team': 1, 'sid': 'qdwderwekmSIvEBaAAAB'}}, {'card': {'color': 3, 'value': 12}, 'player': {'name': 'mathias', 'team': 0, 'sid': '1j5fKRlJ9RyKONgJAAAD'}}, {'card': {'color': 3, 'value': 11}, 'player': {'name': 'helios', 'team': 1, 'sid': 'J1RTyB8TaKd9NxSmAAAF'}}, {'card': {'color': 3, 'value': 8}, 'player': {'name': 'magathe', 'team': 0, 'sid': 'bxRbaqkv4dguxVOVAAAH'}}], [{'card': {'color': 0, 'value': 7}, 'player': {'name': 'magathe', 'team': 0, 'sid': 'bxRbaqkv4dguxVOVAAAH'}}, {'card': {'color': 1, 'value': 9}, 'player': {'name': 'guillaume', 'team': 1, 'sid': 'qdwderwekmSIvEBaAAAB'}}, {'card': {'color': 0, 'value': 12}, 'player': {'name': 'mathias', 'team': 0, 'sid': '1j5fKRlJ9RyKONgJAAAD'}}, {'card': {'color': 0, 'value': 10}, 'player': {'name': 'helios', 'team': 1, 'sid': 'J1RTyB8TaKd9NxSmAAAF'}}]]]
                self.cardOnTable = []

                for p in self.players:
                    p.cardReactionTime = [random.randint(2, 20) for _ in range(4 * 8)]

                if current_app.config["DEBUG_MODE_FAKE_BELOTE"] != -1:
                    self.belote = current_app.config["DEBUG_MODE_FAKE_BELOTE"]
                    logger.debug(f"Fake belote: {self.belote}")

                self.flushCardOnTable()
                self.computeTableAck(self.nextTurn)

        self.sendRoundInfo()

    def restart(self):
        # Get all card
        for p in self.players:
            self.cards += p.cards.copy()
            p.cards = []
        self.attachedGameManger.getGameByID(self.attachedGameID).startNewRound()

    def registerTalkPass(self, player):
        self.registerTalk(player, {}, type="pass")

    def registerTalkContrer(self, player):
        self.registerTalk(player, {}, type="contrer")

    def registerTalkSurContrer(self, player):
        self.registerTalk(player, {}, type="surcontrer")

    def registerTalk(self, player, talk, type=None):
        if not(type != None or ("selectedColor" in talk and "selectedValue" in talk)):
            # Mauvais format de talk
            return
        if self.state == ROUND_STATE_TALKING:
            if self.nextTalk == player:
                flag_next = 0
                flag_end = 0
                if type == None:
                    newValue = int(talk['selectedValue'])

                    if self.talk == {} or self.talk['value'] < newValue and not("contrer" in self.talk):
                        if len(self.talk) > 0:
                            self.lastTalk.append(self.talk)
                        self.talk = {"color": int(talk['selectedColor']), "value": newValue, "player": player}
                        flag_next = 1
                else:
                    if type == "pass":
                        flag_next = 1
                    elif self.talk != {} and type == "contrer":
                        if self.talk['player'].team != player.team:
                            self.talk['contrer'] = player
                            self.contrer = 1
                            flag_next = 1
                    elif self.talk != {} and type == "surcontrer":
                        if "contrer" in self.talk.keys() and self.talk['contrer'].team != player.team:
                            self.talk['surcontrer'] = player
                            self.surcontrer = 1
                            flag_end = 1

                if flag_next:
                    self.nextTalkIndex += 1
                    self.nextTalkIndex %= 4
                    if self.nextTalkIndex == (self.firstDistribIndex + 1) % 4 and self.talk == {}:
                        self.restart()
                        return

                    self.nextTalk = self.players[self.nextTalkIndex]

                    if self.talk != {} and "contrer" in self.talk and self.talk['contrer'] == self.nextTalk:
                        flag_end = 1

                    if self.talk != {} and self.nextTalk == self.talk['player'] and not("contrer" in self.talk):
                        flag_end = 1

                    self.sendRoundInfo()

                if flag_end:
                    self.state = ROUND_STATE_PLAYING
                    # Trier les cartes des joueurs et chercher une belote et compter les points
                    for p in self.players:
                        p.cards = sorted(p.cards, key=lambda x: (x["color"], getBeloteValue(x, self.talk["color"])), reverse=True)
                        p.sendDeck()

                        idx = 0
                        for c in p.cards:
                            if c["color"] == self.talk["color"]:
                                if c["value"] == 12 or c["value"] == 13:
                                    idx += 1
                        if idx == 2:
                            logger.info("Belote détectée (TEAM %d)", p.team)
                            self.belote = p.team

                    self.cardReactionTimeBegin = time.time()
                    self.sendRoundInfo()

    @staticmethod
    def compareCard(card1, card2, trump):
        card1FakeValue = getBeloteValue(card1, trump)
        card2FakeValue = getBeloteValue(card2, trump)
        if card1FakeValue < card2FakeValue:
            return -1
        if card1FakeValue > card2FakeValue:
            return 1
        if card1FakeValue == card2FakeValue:
            return 0

    def computeNewCard(self, player, card):
        currentTrump = self.talk['color']
        # Premier tour
        if len(self.cardOnTable) == 0:
            self.askedColor = card['color']
            self.winningTeam = player.team
            self.winningPlayer = player
            self.winningCard = card
            return True
        else:
            # Atout
            if self.askedColor == currentTrump:
                if card["color"] == self.askedColor:
                    if self.compareCard(card, self.winningCard, currentTrump) > 0:
                        self.winningCard = card
                        self.winningTeam = player.team
                        self.winningPlayer = player
                    else:
                        res, upperCard = player.hasUpper(self.winningCard, currentTrump)
                        if res and upperCard != card:
                            self._emitBroadcast("launch-toast", {"message": f"{player.name} il faut monter à l'atout", "category": "danger"})
                            return False
                    return True
                else:
                    return not(player.hasColor(self.askedColor))


            # Non-atout
            else:
                if card['color'] == self.askedColor:
                    if self.compareCard(card, self.winningCard, currentTrump) > 0:
                        self.winningCard = card
                        self.winningTeam = player.team
                        self.winningPlayer = player
                    return True
                elif card['color'] == currentTrump:
                    if player.hasColor(self.askedColor):
                        self._emitBroadcast("launch-toast", {"message": f"{player.name} a essayé de tricher", "category": "danger"})
                        return False

                    if self.compareCard(card, self.winningCard, currentTrump) > 0:
                        self.winningCard = card
                        self.winningTeam = player.team
                        self.winningPlayer = player
                    else:
                        res, upperCard = player.hasUpper(self.winningCard, currentTrump)
                        if res and upperCard != card:
                            self._emitBroadcast("launch-toast", {"message": f"{player.name} a essayé de tricher", "category": "danger"})
                            return False
                    return True

                else:
                    if self.winningTeam == player.team:
                        return not(player.hasColor(self.askedColor))
                    else:
                        return not(player.hasColor(self.askedColor) or player.hasColor(currentTrump))

    def computeTableAck(self, player):
        if self.needTableAck:
            if player == self.nextTurn:
                self.needTableAck = 0
                self.tableAckTime = time.time_ns()
                self.cardOnTable = []
                self.cardReactionTimeBegin = time.time()

                if len(self.heapTeam[0]) + len(self.heapTeam[1]) >= 8:
                    score = [0, 0]
                    for t in (0, 1):
                        if self.winningTeam == t:
                            score[t] += 10 # 10 de Der
                        for trick in self.heapTeam[t]:
                            for c in trick:
                                score[t] += getBelotePoint(c["card"], self.talk["color"])

                    self.attachedGameManger.getGameByID(self.attachedGameID).registerScore(score, belote=self.belote)
                    return

        self.sendRoundInfo()

    def flushCardOnTable(self):
        self.heapTeam[self.winningTeam].append(self.cardOnTable)
        self.needTableAck = 1

        for index, p in enumerate(self.players):
            if p == self.winningPlayer:
                return index
        return 0


    def cardPlayed(self, player, card, index):
        if(self.state == ROUND_STATE_PLAYING):
            if self.needTableAck or time.time_ns() - self.tableAckTime <= TALBE_ACK_COOLDOWN_NS:
                if time.time_ns() - self.tableAckTime <= TALBE_ACK_COOLDOWN_NS:
                    return {"category": "danger", "message": f"Cooldown anti-missclick ({(time.time_ns() - self.tableAckTime) / (10 ** 9)} s)"}
                else:
                    return {"category": "danger", "message": "Impossible de jouer cette carte"}
            if(player == self.nextTurn):
                #Verifier si la carte est dans le jeu du joueur
                if card == player.cards[index]:
                    result = self.computeNewCard(player, card)
                    self.nextTurn.cardReactionTime.append(time.time() - self.cardReactionTimeBegin)
                    self.cardReactionTimeBegin = time.time()
                    print(f"Reaction time: {self.nextTurn.cardReactionTime[-1]}")
                    if result:
                        played_card = player.cards.pop(index)
                        player.sendDeck()

                        self.cardOnTable.append({"card": played_card, "player": player})

                        if len(self.cardOnTable) >= 4:
                            self.nextTurnIndex = self.flushCardOnTable()

                            self.nextTurn = self.players[self.nextTurnIndex]
                            self.sendRoundInfo()
                            return



                        self.nextTurnIndex = (self.nextTurnIndex + 1) % 4
                        self.nextTurn = self.players[self.nextTurnIndex]
                self.sendRoundInfo()
