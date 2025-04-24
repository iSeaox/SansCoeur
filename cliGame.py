import json
import time
import argparse
import tempfile
from pathlib import Path

# Configuration des chemins de communication
COMMAND_DIR = Path(tempfile.gettempdir()) / "sanscoeur_cmd"
RESPONSE_DIR = Path(tempfile.gettempdir()) / "sanscoeur_resp"
STATUS_FILE = RESPONSE_DIR / "status.json"

class SansCoeurLocalClient:
    def __init__(self):
        """Initialization of the local client"""

        COMMAND_DIR.mkdir(exist_ok=True)
        RESPONSE_DIR.mkdir(exist_ok=True)
        self.command_id = int(time.time() * 1000)

        print(f"IPC COMMAND_DIR : {COMMAND_DIR}")
        print(f"IPC RESPONSE_DIR : {RESPONSE_DIR}")
        print(f"IPC STATUS_FILE : {STATUS_FILE}")

    def send_command(self, command_type, data=None):
        """Sends a command to the server via a file"""
        command = {
            "id": self.command_id,
            "type": command_type,
            "data": data or {},
            "timestamp": time.time()
        }

        self.command_id += 1

        command_file = COMMAND_DIR / f"cmd_{command['id']}.json"
        with open(command_file, 'w') as f:
            json.dump(command, f)

        print(f"Command Sent: {command_type}")
        return command['id']

    def wait_for_response(self, command_id, timeout=10):
        """Waits for a response for the specified command"""
        response_file = RESPONSE_DIR / f"resp_{command_id}.json"
        start_time = time.time()

        while time.time() - start_time < timeout:
            if response_file.exists():
                try:
                    with open(response_file, 'r') as f:
                        response = json.load(f)

                    response_file.unlink()
                    return response
                except Exception as e:
                    print(f"Error reading the response: {e}")
                    return None

            if STATUS_FILE.exists():
                try:
                    with open(STATUS_FILE, 'r') as f:
                        status = json.load(f)
                    print(f"Server status: {status.get('status', 'Unknown')}")
                except:
                    pass

            time.sleep(0.5)

        print(f"Timeout exceeded for command {command_id}")
        return None

    def list_games(self):
        """Lists available games"""
        cmd_id = self.send_command("list_games")
        response = self.wait_for_response(cmd_id)

        if response and "games" in response:
            print("-" * 60)
            print(f"{'ID':<10} {'Status':<15} {'Players':<10} {'Score':<20}")
            print("-" * 60)
            for game in response["games"]:
                status_text = ['Waiting', 'In Progress', 'Finished'][game.get('status', 0)]
                player_count = len(game.get('players', []))
                score = ', '.join(map(str, game.get('score', []))) if isinstance(game.get('score', []), list) else game.get('score', 'N/A')
                print(f"{str(game['id']):<10} {status_text:<15} {(str(player_count) + '/4'):<10} {score:<20}")

            print("-" * 60)
        else:
            print("Unable to retrieve the list of games")

    def create_game(self):
        """Creates a new game"""
        cmd_id = self.send_command("create_game")
        response = self.wait_for_response(cmd_id)

        if response and response.get("success", False):
            print(f"Game successfully created! ID: {response.get('game_id')}")
        else:
            error_msg = response.get("message", "Unknown error") if response else "No response from the server"
            print(f"Unable to create the game: {error_msg}")

        self.list_games()

def main():
    parser = argparse.ArgumentParser(description="Local client for Sans Coeur Online")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.add_parser("list", help="List available games")

    subparsers.add_parser("create", help="Create a new game")

    args = parser.parse_args()

    client = SansCoeurLocalClient()

    if args.command == "list":
        client.list_games()
    elif args.command == "create":
        client.create_game()
    else:
        parser.print_help()

    return 0

if __name__ == "__main__":
    exit(main())