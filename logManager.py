import os
import json
import time
import logging
logger = logging.getLogger(f"app.{__name__}")

from encoder.gameDataEncoder import GameDataEncoder

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
        logger.info(f"Log file: {file_path}")
        if not(os.path.exists(path)):
            logger.error(f"Can't find {path} => created")
            os.makedirs(path)

        if not(os.path.exists(file_path)):
            logger.error(f"Can't find {file_path} => created")
            with open(file_path, "w") as file:
                json.dump([], file, indent=4)

    def logChat(self, chat):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        data = f'[{current_time}] <{chat["player"]["name"]}> {chat["message"]}'

        logger.debug(data)

        with open(self.chat_file_path, "a") as file:
            file.write(data + "\n")

    def logGame(self, game):
        game_data = game.dumpGameInfo()

        duration = time.time() - game.beginTime
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        game_data.update({"time": current_time})
        game_data.update({"duration": duration})

        logs = []
        with open(self.game_file_path, "r+") as file:
            logs = json.load(file)

        if logs != []:
            logs.append(game_data)
            with open(self.game_file_path, "w") as file:
                json.dump(logs, file, indent=4, cls=GameDataEncoder)

        self.printGameSummary(game_data)

    def printGameSummary(self, game_data):
        status = "En attente" if game_data["status"] == 0 else "En cours" if game_data["status"] == 1 else "Termine"
        ready_to_start = "Oui" if game_data["readyToStart"] else "Non"

        summary = (
            "\n==================== Resume de la Partie ====================\n\n"
            f"Joueurs:\n" +
            "\n".join([f"Nom: {player['name']}, Equipe: {player['team']}" for player in game_data["players"]]) +
            f"\n\nScores:\nEquipe 0 : {game_data['score'][0]}\nEquipe 1 : {game_data['score'][1]}\n\n"
            "Scores des manches:\n" +
            "\n".join([f"Manche {game_data['round_score'].index(round_score) + 1}: {round_score['score']}" for round_score in game_data['round_score']]) +
            f"\n\nStatut du jeu : {status}\nPret a commencer : {ready_to_start}\n"
            "=============================================================="
        )

        logger.info(summary)

    def getLastGameData(self):
        with open(self.game_file_path, 'r') as file:
            logs = json.load(file)
        if logs:
            return logs[-1]
        return None

    def dumpGameLogs(self):
        logs = None
        with open(self.game_file_path, 'r') as file:
            logs = json.load(file)
        if logs:
            return logs
        return None