
from flask_socketio import emit
from flask import request, session
from auth import socketio_login_required

def register_handlers(socketio, clients, game_instance):

    @socketio.on("connect")
    @socketio_login_required
    def handle_connect():
        emit('login_success', {"message": "Succesfully logged"}, room=request.sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        pass