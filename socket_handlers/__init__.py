from . import game_handlers, admin_handlers, info_handlers

def init_socket_handlers(socketio, clients, gManager, dbManager):
    """ Initialize all event handler"""
    game_handlers.register_handlers(socketio, clients, gManager)
    admin_handlers.register_handlers(socketio, clients, gManager, dbManager)
    info_handlers.register_handlers(socketio, clients, gManager, dbManager)