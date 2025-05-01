from flask_socketio import emit
from flask import request, url_for
from auth import socketio_admin_required
from flask_login import current_user

from werkzeug.security import generate_password_hash

import statisticManager
import re
import logging
logger = logging.getLogger(f"app.{__name__}")

def _formatUserData(users):
    """
    Format the user data for display.
    """
    formatted_data = []
    for user in users:
        formatted_data.append({
            "username": user.username,
            "registered_on": user.creation_time if user.creation_time else "N/A",
            "last_login": user.last_connection if user.last_connection else "N/A",
            "is_admin": user.is_admin,
            "password_needs_update": user.password_needs_update,
        })
    return formatted_data


def register_handlers(socketio, logManager, gameManager, dbManager, socketMonitor):

    @socketio.on("connect", namespace="/admin")
    @socketio_admin_required
    def handle_admin_connect():
        logger.info(f"{current_user.username} est connecté au namespace admin (SID {request.sid})")
        socketMonitor.register_connection("/admin", current_user.username, request)

    @socketio.on("disconnect", namespace="/admin")
    @socketio_admin_required
    def handle_admin_connect():
        logger.info(f"{current_user.username} est s'est déconnecté du namespace admin (SID {request.sid})")
        socketMonitor.unregister_connection("/admin", current_user.username)

    @socketio.on("get_players", namespace="/admin")
    @socketio_admin_required
    def handle_get_players():
        """Récupère la liste des joueurs inscrits"""
        users = dbManager.getAllUsers()

        players_data = []
        for user in users:
            players_data.append({
                "username": user.username,
                "registered_on": user.creation_time if user.creation_time else "N/A",
                "last_login": user.last_connection if user.last_connection else "N/A",
                "is_admin": user.is_admin,
                "password_needs_update": user.password_needs_update,
            })

        emit("players_list", {"players": players_data}, namespace="/admin")

    @socketio.on("delete_player", namespace="/admin")
    @socketio_admin_required
    def handle_delete_player(data):
        username = data.get("username")
        if not username:
            emit("launch-toast", {"message": "Username is required", "category": "danger"}, namespace="/info", room=current_user.username)
            return

        ret, err = dbManager.deleteUser(username)
        if not ret:
            emit("launch-toast", {"message": f"Error deleting user: {err}", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        emit("launch-toast", {"message": f"User {username} deleted successfully", "category": "success"}, namespace="/info", room=current_user.username)
        emit("players_list", {"players": _formatUserData(dbManager.getAllUsers())}, namespace="/admin")

    @socketio.on("update_flag", namespace="/admin")
    @socketio_admin_required
    def handle_update_flag(data):
        username = data.get("username")
        if not username:
            emit("launch-toast", {"message": "Username is required", "category": "danger"}, namespace="/info", room=current_user.username)
            return

        ret, err = dbManager.updateUserPasswordFlag(username, 1)
        if not ret:
            emit("launch-toast", {"message": f"Error updating user: {err}", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        emit("launch-toast", {"message": f"User {username} updated successfully", "category": "success"}, namespace="/info", room=current_user.username)
        emit("players_list", {"players": _formatUserData(dbManager.getAllUsers())}, namespace="/admin")

    @socketio.on("add_player", namespace="/admin")
    @socketio_admin_required
    def handle_add_player(data):
        username = data.get("username")
        if not username:
            emit("launch-toast", {"message": "Username is required", "category": "danger"}, namespace="/info", room=current_user.username)
            return

        existing_user = dbManager.getUserByName(username)
        if existing_user:
            emit("launch-toast", {"message": f"User {username} already exists", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        hashed_password = generate_password_hash(username[0])

        ret, err = dbManager.insertUser(username, hashed_password, 1)
        if not ret:
            emit("launch-toast", {"message": f"Error adding user: {err}", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        emit("launch-toast", {"message": f"User {username} added successfully", "category": "success"}, namespace="/info", room=current_user.username)
        emit("players_list", {"players": _formatUserData(dbManager.getAllUsers())}, namespace="/admin")

    @socketio.on("get_games", namespace="/admin")
    @socketio_admin_required
    def handle_get_games():
        emit("games_list", {"games": gameManager.getGames()}, namespace="/admin")

    @socketio.on("get_connections", namespace="/admin")
    @socketio_admin_required
    def handle_get_connections():
        emit("connections_list", {"connections": socketMonitor.resolve_rooms(socketio)}, namespace="/admin")

    @socketio.on("delete_game", namespace="/admin")
    @socketio_admin_required
    def handle_delete_game(data):
        gameID = int(data.get("gameID"))
        if not gameID:
            emit("launch-toast", {"message": "Game ID is required", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        game = gameManager.getGameByID(gameID)
        if not game:
            emit("launch-toast", {"message": f"Game {gameID} not found", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        ret, err = gameManager.deleteGame(game)
        if not ret:
            emit("launch-toast", {"message": f"Error deleting game: {err}", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        emit("launch-toast", {"message": f"Game {gameID} deleted successfully", "category": "success"}, namespace="/info", room=current_user.username)
        emit("games_list", {"games": gameManager.getGames()}, namespace="/admin")

    @socketio.on("new_game", namespace="/admin")
    @socketio_admin_required
    def handle_new_game():
        ret = gameManager.registerNewGame()
        emit("launch-toast", {"message": f"New game created with ID {ret}", "category": "success"}, namespace="/info", room=current_user.username)
        emit("games_list", {"games": gameManager.getGames()}, namespace="/admin")

    @socketio.on("update_score", namespace="/admin")
    @socketio_admin_required
    def handle_update_score(data):
        gameID = int(data.get("gameId"))
        score = data.get("score")

        if not gameID or not score:
            emit("launch-toast", {"message": "Game ID and score are required", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        game = gameManager.getGameByID(gameID)
        if not game:
            emit("launch-toast", {"message": f"Game {gameID} not found", "category": "danger"}, namespace="/info", room=current_user.username)
            return
        game.score = score
        emit("launch-toast", {"message": f"Game {gameID} updated successfully", "category": "success"}, namespace="/info", room=current_user.username)
        emit("games_list", {"games": gameManager.getGames()}, namespace="/admin")