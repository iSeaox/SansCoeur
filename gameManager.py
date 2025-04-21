import game
from flask_socketio import emit
from flask import url_for
import warnings
import logging
logger = logging.getLogger(f"app.{__name__}")

warnings.simplefilter("always", DeprecationWarning)

class GameManager:
    def __init__(self, logManager, roomManager):
        self.logManager = logManager
        self.roomManager = roomManager
        self.games = []

    def overrideGame(self, game):
        self.deleteGame(game)
        self.registerNewGame()

    def deleteGame(self, game):
        logger.info("Supression de ", game)

        self.roomManager.broadcast_to_room(
            f"game-{game.id}", 'end_game',
             {"redirect": url_for('index')}
        )

        self.roomManager.delete_room(f"game-{game.id}")
        self.roomManager.delete_room(f"game-{game.id}-spec")

        self.games.remove(game)
        del game

    def registerNewGame(self):
        newGame = game.Game(self, self.logManager)
        logger.info(f"Création de {newGame}")

        self.games.append(newGame)
        logger.info(f"Stack de Game: {self.games}")

    def getGameByID(self, id):
        for g in self.games:
            if g.id == id:
                return g

    def getGameByPlayerName(self, name):
        for g in self.games:
            if g.getPlayerByName(name) != None:
                return g
        return None


    # TODO : DEPRECATED FUNCTION
    def getGame(self):
        warnings.warn(
        "Deprecated functin should be removed", category=DeprecationWarning, stacklevel=0)
        if len(self.games) > 0:
            return self.games[0]

    def getGames(self):
        out = []
        for game in self.games:
            out.append(game.dumpGameInfo())

        return out

    def updateClients(self):
        games = self.getGames()
        emit('update_games', {'games': games}, broadcast=True)