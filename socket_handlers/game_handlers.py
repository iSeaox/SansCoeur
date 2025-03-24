from flask_socketio import emit
from flask import request
from auth import socketio_login_required
from flask_login import current_user

def register_handlers(socketio, connected_clients, currentGame):

    @socketio.on("connect")
    @socketio_login_required
    def handle_connect():
        currentGame.broadcastGameInfo()

    @socketio.on('join_game')
    @socketio_login_required
    def handle_join_game(data):
        name = current_user.username
        team = data.get('team')

        if team not in [0, 1]:
            emit('join_error', {'message': 'Team doit être 0 ou 1'})
            return

        result, message = currentGame.registerPlayer(name, team, request.sid)
        if result:
            print(f'Client {name} a rejoint la Team {team}')
            emit('join_success', {'message': f'Vous avez rejoint la Team {team} !'})
            currentGame.broadcastGameInfo()
        else:
            emit('join_error', {'message': message})

    @socketio.on('start_game')
    @socketio_login_required
    def handle_start_game():
        result, message = currentGame.start()
        if not(result):
            emit('start_game_error', {'message': message})
            return
        currentGame.broadcastGameInfo()

    @socketio.on('disconnect')
    def handle_disconnect():
        pass