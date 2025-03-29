from flask_socketio import emit

ROUND_STATE_SETUP = 0
ROUND_STATE_TALKING = 1
ROUND_STATE_PLAYING = 2
class Round:

    def __init__(self, players, firstDistribIndex, cards):
        self.players = players
        self.firstDistribIndex = firstDistribIndex
        self.currentTurn = 0
        self.cards = cards
        self.state = ROUND_STATE_SETUP
        self.nextTurnIndex = 0
        self.nextTurn = self.players[self.nextTurnIndex]
        self.cardOnTable = []
        self.nextTalkIndex = 0
        self.nextTalk = self.players[self.nextTalkIndex]
        self.talk = {}
        self.contrer = 0
        self.surcontrer = 0

    def dumpRoundInfo(self):
        print(self.talk)
        out = {
            "state": self.state,
        }
        if self.talk != {}:
            out.update({
                "current_talk": {
                    "color": self.talk['color'],
                    "value": self.talk['value'],
                    "player": self.talk['player'].name
                }
            })

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
                "card_on_table": self.cardOnTable
            })
        else:
            pass
        return out

    def sendRoundInfo(self):
        emit('round_info', self.dumpRoundInfo(), broadcast=True)

    def cardsDistrib(self):
        # TODO: Pensez à couper le jeu
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
        # TODO : DEBUG
        # self.state = ROUND_STATE_PLAYING
        # self.talk =  {"color": 2, "value": 100, "player": self.players[0]}
        # self.sendRoundInfo()

    def restart(self):
        self.state = ROUND_STATE_SETUP

        # Get all card
        for p in self.players:
            self.cards += p.cards.copy()
            p.cards = []

        self.start()


    def registerTalkPass(self, player):
        self.registerTalk(player, {}, type="pass")

    def registerTalkContrer(self, player):
        self.registerTalk(player, {}, type="contrer")

    def registerTalkSurContrer(self, player):
        self.registerTalk(player, {}, type="surcontrer")

    def registerTalk(self, player, talk, type=None):
        if not(type != None or ("color" in talk and "value" in talk)):
            # Mauvais format de talk
            return
        if self.state == ROUND_STATE_TALKING:
            if self.nextTalk == player:
                flag_next = 0
                flag_end = 0
                if type == None:
                    newValue = int(talk['selectedValue'])

                    if self.talk == {} or self.talk['value'] < newValue and not("contrer" in self.talk):
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
                            print("END SUR CONTERR")
                            flag_end = 1

                if flag_next:
                    self.nextTalkIndex += 1
                    self.nextTalkIndex %= 4
                    if self.nextTalkIndex == 0 and self.talk == {}:
                        self.restart()
                        return

                    self.nextTalk = self.players[self.nextTalkIndex]

                    if self.talk != {} and "contrer" in self.talk and self.talk['contrer'] == self.nextTalk:
                        print("END CONTREE")
                        flag_end = 1

                    if self.talk != {} and self.nextTalk == self.talk['player'] and not("contrer" in self.talk):
                        print("END CLASSIC")
                        flag_end = 1

                    self.sendRoundInfo()

                if flag_end:
                    self.state = ROUND_STATE_PLAYING
                    self.sendRoundInfo()

    def cardPlayed(self, player, card, index):
        print("CARD PLAYED : ", player, " | ", card)
        if(self.state == ROUND_STATE_PLAYING):
            if(player == self.nextTurn):
                if len(self.cardOnTable) >= 4:
                    # TODO : END THE HAND
                    pass
                else:
                    # TODO : CHECK IF CARD CAN BE PLAYED
                    played_card = player.cards.pop(index)
                    player.sendDeck()

                    self.cardOnTable.append(played_card)
                    self.nextTurnIndex = (self.nextTurnIndex + 1) % 4
                    self.nextTurn = self.players[self.nextTurnIndex]
                self.sendRoundInfo()
