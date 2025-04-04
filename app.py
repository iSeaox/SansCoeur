import sys
import datetime
from pathlib import Path

# To manage import to top-level
sys.path.append(str(Path(__file__).parent))

import gameManager
import logManager
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ################################################
# Flask Setup
app = Flask(__name__)
app.config.from_pyfile('config.py')

socketio = SocketIO(app, cors_allowed_origins="*")

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

logManager = logManager.LogManager("./logs", "logs.json", "chat.log")
currentGameManager = gameManager.GameManager(logManager)
currentGameManager.registerNewGame()


connected_clients = {}

# ################################################
# Socket Handlers
from socket_handlers import init_socket_handlers
init_socket_handlers(socketio, connected_clients, currentGameManager)

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
    return render_template("dashboard.html", username=current_user.username)

# ################################################
# Main

if __name__ == "__main__":
    # ! DEBUG : Connexion auto des joueurs
    # currentGameManager.getGame().registerPlayer("magathe", 0, None)
    # currentGameManager.getGame().registerPlayer("helios", 1, None)
    # currentGameManager.getGame().registerPlayer("mathias", 0, None)

    socketio.run(app, debug=True, host="0.0.0.0", port=25565)
