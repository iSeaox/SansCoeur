from flask_socketio import emit, join_room, leave_room
from flask import request, url_for
from auth import socketio_login_required
from flask_login import current_user
import statisticManager
import re
import logging
logger = logging.getLogger(f"app.{__name__}")

def register_handlers(socketio, socketMonitor):

    @socketio.on("connect", namespace="/info")
    @socketio_login_required
    def handle_info_connect():
        logger.info(f"{current_user.username} est connecté au namespace info (SID {request.sid})")
        join_room(current_user.username)
        socketMonitor.register_connection("/info", current_user.username, request)

    @socketio.on("disconnect", namespace="/info")
    @socketio_login_required
    def handle_info_connect():
        logger.info(f"{current_user.username} s'est déconnecté au namespace info (SID {request.sid})")
        leave_room(current_user.username)
        socketMonitor.unregister_connection("/info", current_user.username)

