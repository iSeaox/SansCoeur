import os
import json
import time

class LogManager:
    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        self.file_path = os.path.join(self.path, self.filename)
        print("[INFO] Log file:", self.file_path)
        if not(os.path.exists(self.path)):
            print(f"[INFO] Cant't find {self.path} => created")
            os.makedirs(self.path)

        if not(os.path.exists(self.file_path)):
            print(f"[INFO] Cant't find {self.file_path} => created")
            with open(self.file_path, "w") as file:
                json.dump([], file, indent=4)

    def logGame(self, game):
        game_data = game.dumpGameInfo()

        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # temps actuel au format lisible
        game_data.update({"time": current_time})

        with open(self.file_path, "r+") as file:
            logs = json.load(file)
            logs.append(game_data)
            file.seek(0)
            json.dump(logs, file, indent=4)

        self.printGameSummary(game_data)

    def printGameSummary(self, game_data):
        print("\n==================== Résumé de la Partie ====================")

        print("\nJoueurs:")
        for player in game_data["players"]:
            print(f"Nom: {player['name']}, Équipe: {player['team']}")

        print("\nScores:")
        print(f"Équipe 0 : {game_data['score'][0]}")
        print(f"Équipe 1 : {game_data['score'][1]}")

        print("\nScores des manches:")
        for round_score in game_data['round_score']:
            print(f"Manche {game_data['round_score'].index(round_score) + 1}: {round_score['score']}")


        status = "En attente" if game_data["status"] == 0 else "En cours" if game_data["status"] == 1 else "Terminé"
        print(f"\nStatut du jeu : {status}")


        ready_to_start = "Oui" if game_data["readyToStart"] else "Non"
        print(f"Prêt à commencer : {ready_to_start}")

        print("\n==============================================================")

    def getLastGameData(self):
        with open(self.file_path, 'r') as file:
            logs = json.load(file)
        if logs:
            return logs[-1]
        return None