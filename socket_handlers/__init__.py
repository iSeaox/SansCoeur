from . import game_handlers, admin_handlers, info_handlers

def init_socket_handlers(socketio, clients, gManager, dbManager, socketMonitor, currentBotDiscord):
    """ Initialize all event handler"""

    socketMonitor.add_socket("/")
    socketMonitor.add_socket("/admin")
    socketMonitor.add_socket("/info")

    game_handlers.register_handlers(socketio, clients, gManager, socketMonitor, currentBotDiscord, dbManager)
    admin_handlers.register_handlers(socketio, clients, gManager, dbManager, socketMonitor)
    info_handlers.register_handlers(socketio, socketMonitor)