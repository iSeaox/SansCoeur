import sys
import datetime
from pathlib import Path

from werkzeug.middleware.proxy_fix import ProxyFix

# To manage import to top-level
sys.path.append(str(Path(__file__).parent))

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ################################################
# Loggin setup

import logging
import logging.config
import json
import os

def setup_logging(
        default_path='logging_config.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'):

    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    path = os.getenv(env_key, default_path)
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

setup_logging()
logger = logging.getLogger(f"app.{__name__}")
# ################################################
# Flask Setup
app = Flask(__name__)
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)

socketio = SocketIO(app, cors_allowed_origins="*")
# ################################################
# Setup

import gameManager
import logManager
import roomManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = ''

# ################################################
# BDD
# TODO : Setup real BDD

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = {
    1: User(1, 'guillaume', generate_password_hash('g')),
    2: User(2, 'mathias', generate_password_hash('m')),
    3: User(3, 'helios', generate_password_hash('h')),
    4: User(4, 'magathe', generate_password_hash('m')),
    5: User(5, 'jocelyn', generate_password_hash('j')),
    6: User(6, 'esthelle', generate_password_hash('e')),
    7: User(7, 'pauline', generate_password_hash('p')),
    8: User(8, 'christian', generate_password_hash('c')),
    9: User(9, 'bastien', generate_password_hash('b')),
    10: User(10, 'nico', generate_password_hash('n')),
    11: User(11, 'mathis', generate_password_hash('m')),
    12: User(12, 'lucas', generate_password_hash('l')),
}

# ################################################
# Global Variables

currentlogManager = logManager.LogManager("./logs", "logs.json", "chat.log")
currentRoomManager = roomManager.RoomManager(socketio)
currentGameManager = gameManager.GameManager(currentlogManager, currentRoomManager)
currentGameManager.registerNewGame()

# ################################################
# Socket Handlers
from socket_handlers import init_socket_handlers
import argparse
init_socket_handlers(socketio, currentlogManager, currentGameManager)

# ################################################
# App routine

# ___________________________________________
# Login
@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))
# ___________________________________________

@app.route("/")
@login_required
def index():
    return render_template("games.html", username=current_user.username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = next((u for u in users.values() if u.username == username), None)

        if user and check_password_hash(user.password, password):
            remember = request.form.get('remember') == 'on'
            login_user(user, remember=remember)
            flash('Connexion réussie !', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Identifiant ou mot de passe incorrect', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'secondary')
    return redirect(url_for('index'))

@app.route("/sound")
def sound():
    return render_template("sound.html")

@app.route("/dashboard")
@login_required
def dashboard():
    game_id = request.args.get('id')
    if not game_id or not currentGameManager.getGameByID(int(game_id)):
        return render_template("errors/game_not_found.html",
                              message="Partie introuvable",
                              username=current_user.username)
    game = currentGameManager.getGameByID(int(game_id))

    player = game.getPlayerByName(current_user.username)
    if not player:
        socketio.emit("launch-toast",
                     {"message": f"{current_user.username} regarde la partie",
                      "category": "success"},
                     room=f"game-{game.id}")

    return render_template("dashboard.html", username=current_user.username)

# ################################################
# Main

if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="SansCoeur Game Server")
    parser.add_argument("--players", "-p", action="store_true", help="Enable auto player connection")
    parser.add_argument("--talk-pass", "-t", action="store_true", help="Pass talk phase")
    parser.add_argument("--fake-rounds", "-r", action="store_true", help="Register fake rounds")
    parser.add_argument("--cards", "-c", action="store_true", help="Place cards on table")
    parser.add_argument("--end-game", "-e", action="store_true", help="End game at start (quite weird isn't it ?)")
    parser.add_argument("--belote", "-b", type=int, help="Start the game with a fake belote (provide Team ID 0 or 1)")
    args = parser.parse_args()

    if args.players:
        app.config["DEBUG_MODE"] = 1
        app.config["DEBUG_MODE_PLAYERS"] = 1

    if args.talk_pass:
        app.config["DEBUG_MODE"] = 1
        app.config["DEBUG_MODE_TALKS"] = 1
        app.config["DEBUG_MODE_PLAYERS"] = 1

    if args.cards:
        app.config["DEBUG_MODE"] = 1
        app.config["DEBUG_MODE_TABLE_CARDS"] = 1
        app.config["DEBUG_MODE_TALKS"] = 1
        app.config["DEBUG_MODE_PLAYERS"] = 1

    if args.end_game:
        app.config["DEBUG_MODE"] = 1
        app.config["DEBUG_MODE_END_GAME"] = 1
        app.config["DEBUG_MODE_TALKS"] = 1
        app.config["DEBUG_MODE_PLAYERS"] = 1

    if args.fake_rounds:
        app.config["DEBUG_MODE"] = 1
        app.config["DEBUG_MODE_PLAYERS"] = 1
        app.config["DEBUG_MODE_FAKE_ROUNDS"] = 1

    if args.belote is not None:
        if not args.end_game:
            logger.error("You need to provide --end-game to use --belote")
            sys.exit(1)
        app.config["DEBUG_MODE"] = 1
        app.config["DEBUG_MODE_FAKE_BELOTE"] = args.belote
        app.config["DEBUG_MODE_TALKS"] = 1
        app.config["DEBUG_MODE_PLAYERS"] = 1

    if app.config["DEBUG_MODE_PLAYERS"]:
        currentGameManager.getGame().registerPlayer("magathe", 0, None)
        currentGameManager.getGame().registerPlayer("helios", 1, None)
        currentGameManager.getGame().registerPlayer("mathias", 0, None)

    if app.config["DEBUG_MODE"]:
        logger.warning("GAME STARTED IN DEBUG MODE")

    socketio.run(app, debug=True, host="0.0.0.0", port=25565)
