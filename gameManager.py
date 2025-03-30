import game

class GameManager:
    def __init__(self):
        self.games = []

    def overrideGame(self, game):
        self.deleteGame(game)
        self.registerNewGame()

    def deleteGame(self, game):
        print("Supression de ", game)
        self.games.remove(game)
        del game

    def registerNewGame(self):
        newGame = game.Game(self)
        print("Création de ", newGame)

        self.games.append(newGame)
        print("Stack de Game: ", self.games)

    def getGame(self):
        if len(self.games) > 0:
            return self.games[0]