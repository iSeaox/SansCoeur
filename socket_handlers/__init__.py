from . import game_handlers

def init_socket_handlers(socketio, clients, gManager, sidManager):
    """ Initialize all event handler"""
    game_handlers.register_handlers(socketio, clients, gManager, sidManager)