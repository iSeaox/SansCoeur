from flask_socketio import emit

ROUND_STATE_SETUP = 0
ROUND_STATE_PLAYING = 1
class Round:

    def __init__(self, players, firstDistribIndex, cards):
        self.players = players
        self.firstDistribIndex = firstDistribIndex
        self.currentTurn = 0
        self.cards = cards
        self.state = ROUND_STATE_SETUP
        self.card_played = []
        self.nextTurnIndex = 0
        self.nextTurn = self.players[self.nextTurnIndex]
        self.cardOnTable = []

    def dumpRoundInfo(self):
        return {
            "state": self.state,
            "next_turn": self.nextTurn.name,
            "card_on_table": self.cardOnTable
        }

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

        self.state = ROUND_STATE_PLAYING
        self.sendRoundInfo()

    def cardPlayed(self, player, card, index):
        print("CARD PLAYED : ", player, " | ", card)
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
