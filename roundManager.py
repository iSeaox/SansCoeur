import round

class RoundManager:
    def __init__(self):
        self.rounds = []

    def deleteRound(self, round):
        if round in self.rounds:
            print("Supression de ", round)
            self.rounds.remove(round)
            del round

    def registerNewRound(self, players, firstDistributionIndex, cards, gManager):
        newRound = round.Round(players, firstDistributionIndex, cards, gManager)
        print("[", gManager.getGame(), "] Création de ", newRound)

        self.rounds.append(newRound)
        print("[", gManager.getGame(), "] Stack de Round: ", self.rounds)

    def getRound(self):
        if len(self.rounds) > 0:
            return self.rounds[0]
