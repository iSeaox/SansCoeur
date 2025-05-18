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

import statisticManager
import argparse

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
import dbManager

currentDBManager = dbManager.dbManager(app.config["DATABASE_PATH"])

# ################################################
# Global Variables

currentlogManager = logManager.LogManager("./logs", "logs.json", "chat.log")
currentRoomManager = roomManager.RoomManager(socketio)
currentGameManager = gameManager.GameManager(currentlogManager, currentRoomManager)
currentGameManager.registerNewGame()

# ################################################
# Discord Bot
from botDiscord import BotDiscord

current_bot_discord = BotDiscord()
current_bot_discord.start()

# ################################################
# Socket Handlers
from socketMonitoring import SocketMonitor
currentSocketMonitor = SocketMonitor()

from socket_handlers import init_socket_handlers
init_socket_handlers(socketio, currentlogManager, currentGameManager, currentDBManager, currentSocketMonitor, current_bot_discord)

# ################################################
# App routine

# ___________________________________________
# Login

import auth

@login_manager.user_loader
def load_user(user_id):
    return currentDBManager.getUser(user_id)
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

        user = currentDBManager.getUserByName(username)

        if user and check_password_hash(user.password, password):
            remember = request.form.get('remember') == 'on'
            currentDBManager.updateLoginTime(user.id, datetime.datetime.now())
            login_user(user, remember=remember)
            flash('Connexion réussie !', 'success')

            if user.password_needs_update:
                return redirect(url_for('change_password'))

            return redirect(url_for('index'))
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
    if not game_id.isdigit():
        return render_template("errors/game_not_found.html",
                              message="ID de partie invalide",
                              username=current_user.username)
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

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'danger')
            return render_template('change_password.html')

        success, message = currentDBManager.updatePassword(current_user.id, generate_password_hash(password))

        if success:
            flash(message, 'success')
            logout_user()
            return redirect(url_for('index'))
        else:
            flash(message, 'danger')

    if not current_user.password_needs_update:
        return render_template('errors/change_error.html')
    else:
        return render_template('change_password.html')

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html",
                           user=current_user,
                           statistics=statisticManager.dumpData(currentlogManager, statisticManager.PROFILE_STATISTIC, player=current_user.username),)

@app.route("/admin")
@auth.admin_required
@login_required
def admin():
    return render_template("/admin/dashboard.html", username=current_user.username)

@app.route("/manifest.json")
def manifest():
    with open(app.config["MANIFEST_JSON"], "r", encoding="utf-8") as f:
        manifest_json = json.load(f)
    return manifest_json

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
        currentGameManager.getDebugGame().registerPlayer("magathe", 0, None)
        currentGameManager.getDebugGame().registerPlayer("helios", 1, None)
        currentGameManager.getDebugGame().registerPlayer("mathias", 0, None)

    if app.config["DEBUG_MODE"]:
        logger.warning("GAME STARTED IN DEBUG MODE")

    socketio.run(app, debug=True, host="0.0.0.0", port=25565)
