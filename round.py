from flask_socketio import emit

class Round:
    def __init__(self, players, firstDistribIndex, cards):
        self.players = players
        self.firstDistribIndex = firstDistribIndex
        self.currentTurn = 0
        self.cards = cards

    def sendRoundInfo(self):
        pass

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
