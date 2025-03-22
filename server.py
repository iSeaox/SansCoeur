import game

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

currentGame = game.Game()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # Autorise toutes les origines pour le développement

connected_clients = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connecté')

@socketio.on('login')
def handle_login(data):
    """
    Reçoit le nom du client et le stocke.
    """
    name = data.get('name')

    # Validation du nom
    if not name or not isinstance(name, str):
        emit('login_error', {'message': 'Nom invalide'})
        return

    # Stockage des informations du client (sans team pour l'instant)
    connected_clients[request.sid] = {'name': name, 'team': None}
    print(f'Client {name} connecté')

    # Confirmation de la connexion
    emit('login_success', {'message': f'Bienvenue, {name} !'})
    emit('game_info', currentGame.dumpGameInfo())

@socketio.on('join_game')
def handle_join_game(data):
    """
    Reçoit la team choisie par le client et la stocke.
    """
    team = data.get('team')

    # Validation de la team
    if team not in [0, 1]:
        emit('join_error', {'message': 'Team doit être 0 ou 1'})
        return

    # Mise à jour de la team du client
    if request.sid in connected_clients:
        name = connected_clients[request.sid]['name']
        result, message = currentGame.registerPlayer(name, team, request.sid)
        if result:
            print(f'Client {name} a rejoint la Team {team}')
            emit('join_success', {'message': f'Vous avez rejoint la Team {team} !'})
            currentGame.broadcastGameInfo()
        else:
            emit('join_error', {'message': message})
    else:
        emit('join_error', {'message': 'Vous devez d\'abord vous connecter'})

@socketio.on('request_game_info')
def handle_request_game_info():
    """
    Envoie les informations de la partie en cours au client.
    """
    if request.sid in connected_clients:
        # Préparation des informations de la partie
        game_info = currentGame.dumpGameInfo()
        emit('game_info', game_info)
    else:
        emit('game_info_error', {'message': 'Vous devez d\'abord vous connecter'})

@socketio.on('start_game')
def handle_start_game():
    if request.sid in connected_clients:
        result, message = currentGame.start()
        if not(result):
            emit('start_game_error', {'message': message})
            return
        currentGame.broadcastGameInfo()
    else:
        emit('start_game_error', {'message': 'Vous devez d\'abord vous connecter'})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Supprime le client de la liste des clients connectés lors de la déconnexion.
    """
    client_info = connected_clients.pop(request.sid, None)
    if client_info:
        print(f'Client {client_info["name"]} (Team {client_info["team"]}) déconnecté')

if __name__ == "__main__":

    socketio.run(app, debug=True)