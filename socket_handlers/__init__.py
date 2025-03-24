from . import auth_handlers, game_handlers

def init_socket_handlers(socketio, clients, game_instance):
    """ Initialize all event handler"""
    auth_handlers.register_handlers(socketio, clients, game_instance)
    game_handlers.register_handlers(socketio, clients, game_instance)