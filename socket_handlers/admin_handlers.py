from flask_socketio import emit
from flask import request, url_for
from auth import socketio_admin_required
from flask_login import current_user
import statisticManager
import re
import logging
logger = logging.getLogger(f"app.{__name__}")

def register_handlers(socketio, logManager, gameManager, dbManager):

    @socketio.on("connect", namespace="/admin")
    @socketio_admin_required
    def handle_admin_connect():
        logger.info(f"{current_user.username} est connecté au namespace admin (SID {request.sid})")

    @socketio.on("disconnect", namespace="/admin")
    @socketio_admin_required
    def handle_admin_connect():
        logger.info(f"{current_user.username} est s'est déconnecté du namespace admin (SID {request.sid})")
