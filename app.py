import sys
import datetime
from pathlib import Path

# To manage import to top-level
sys.path.append(str(Path(__file__).parent))

import game
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from auth import socketio_login_required

# ################################################
# Flask Setup
app = Flask(__name__)
app.config.from_pyfile('config.py')

socketio = SocketIO(app, cors_allowed_origins="*")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    4: User(4, 'magathe', generate_password_hash('m'))
}

# ################################################
# Global Variables

currentGame = game.Game()
connected_clients = {}

# ################################################
# Socket Handlers
from socket_handlers import init_socket_handlers
init_socket_handlers(socketio, connected_clients, currentGame)

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
    return render_template("dashboard.html", username=current_user.username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = next((u for u in users.values() if u.username == username), None)

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Connexion réussie!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Identifiant ou mot de passe incorrect', 'danger')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

# ################################################
# Main

if __name__ == "__main__":
    currentGame.registerPlayer("magathe", 0, None)
    currentGame.registerPlayer("helios", 1, None)
    currentGame.registerPlayer("mathias", 0, None)
    socketio.run(app, debug=True)

