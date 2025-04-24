import round
import logging
logger = logging.getLogger(f"app.{__name__}")

class RoundManager:
    def __init__(self):
        self.rounds = []

    def deleteRound(self, round):
        if round in self.rounds:
            logger.info(f"Supression de {round}")
            self.rounds.remove(round)
            del round

    def registerNewRound(self, gameId, players, firstDistributionIndex, cards, gManager):
        newRound = round.Round(players, firstDistributionIndex, cards, gManager, gameId)
        logger.info(f"[{gManager.getGameByID(gameId)}] Création de {newRound}")

        self.rounds.append(newRound)
        newRound.sendRoundInfo()
        logger.info(f"[{gManager.getGameByID(gameId)}] Stack de Round: {self.rounds}")

    def getRound(self):
        if len(self.rounds) > 0:
            return self.rounds[0]
