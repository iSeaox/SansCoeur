import os
import json
import time

class LogManager:
    def __init__(self, path, game_filename, chat_filename):
        self.path = path
        self.game_filename = game_filename
        self.chat_filename = chat_filename
        self.game_file_path = os.path.join(self.path, self.game_filename)
        self.chat_file_path = os.path.join(self.path, self.chat_filename)

        self.checkPath(self.path, self.game_file_path)
        self.checkPath(self.path, self.chat_file_path)

    @staticmethod
    def checkPath(path, file_path):
        print("[INFO] Log file:", file_path)
        if not(os.path.exists(path)):
            print(f"[INFO] Cant't find {path} => created")
            os.makedirs(path)

        if not(os.path.exists(file_path)):
            print(f"[INFO] Cant't find {file_path} => created")
            with open(file_path, "w") as file:
                json.dump([], file, indent=4)

    def logChat(self, chat):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data = f'[{current_time}] <{chat["player"]["name"]}> {chat["message"]}'

        print(data)

        with open(self.chat_file_path, "a") as file:
            file.write(data + "\n")

    def logGame(self, game):
        game_data = game.dumpGameInfo()

        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        game_data.update({"time": current_time})

        with open(self.game_file_path, "r+") as file:
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
        with open(self.game_file_path, 'r') as file:
            logs = json.load(file)
        if logs:
            return logs[-1]
        return None