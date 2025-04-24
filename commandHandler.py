from pathlib import Path
import tempfile
import time
import threading
import json
import logging
logger = logging.getLogger(f"app.{__name__}")

COMMAND_DIR = Path(tempfile.gettempdir()) / "sanscoeur_cmd"
RESPONSE_DIR = Path(tempfile.gettempdir()) / "sanscoeur_resp"
STATUS_FILE = RESPONSE_DIR / "status.json"

COMMAND_DIR.mkdir(exist_ok=True)
RESPONSE_DIR.mkdir(exist_ok=True)

class CommandHandler:
    def __init__(self, gameManager):
        """Initializes the command handler"""
        self.running = False
        self.thread = None
        self.gameManager = gameManager

        logger.info(f"IPC COMMAND_DIR : {COMMAND_DIR}")
        logger.info(f"IPC RESPONSE_DIR : {RESPONSE_DIR}")
        logger.info(f"IPC STATUS_FILE : {STATUS_FILE}")

    def start(self):
        """Starts the command monitoring thread"""
        if self.thread is not None and self.thread.is_alive():
            return

        self.running = True
        self.thread = threading.Thread(target=self.monitor_commands, daemon=True)
        self.thread.start()

        self._update_status("running")

    def stop(self):
        """Stops the monitoring thread"""
        self.running = False
        self._update_status("stopped")
        if self.thread:
            self.thread.join(timeout=2)

    def _update_status(self, status):
        """Updates the status file"""
        with open(STATUS_FILE, 'w') as f:
            json.dump({
                "status": status,
                "timestamp": time.time()
            }, f)

    def monitor_commands(self):
        """Monitors the command directory to process new commands"""
        while self.running:
            try:
                for cmd_file in COMMAND_DIR.glob("cmd_*.json"):
                    try:
                        with open(cmd_file, 'r') as f:
                            command = json.load(f)

                        response = self.process_command(command)

                        resp_file = RESPONSE_DIR / f"resp_{command['id']}.json"
                        with open(resp_file, 'w') as f:
                            json.dump(response, f)

                        cmd_file.unlink()
                    except Exception as e:
                        print(f"Error processing command file {cmd_file}: {e}")
            except Exception as e:
                print(f"Error in command monitor: {e}")

            time.sleep(0.5)

    def process_command(self, command):
        """Processes a command and returns a response"""
        cmd_type = command.get("type", "")
        data = command.get("data", {})
        response = {"id": command.get("id"), "success": False}
        logger.info(f"Processing command: {command}")

        if cmd_type == "list_games":
            response["games"] = self.gameManager.getGames()
            response["success"] = True
        elif cmd_type == "create_game":
            response["game_id"] = self.gameManager.registerNewGame()
            response["success"] = True
        return response