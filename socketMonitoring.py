import logging
logger = logging.getLogger(f"app.{__name__}")

class SocketMonitor:
    def __init__(self):
        self.sockets = {}

    def add_socket(self, socket_name):
        self.sockets[socket_name] = {
            "socket_id": socket_name,
            "status": "active",
            "connections": {},
        }

    def remove_socket(self, socket_id):
        """Remove a socket from the monitoring list."""
        if socket_id in self.sockets:
            del self.sockets[socket_id]
            logger.info(f"Socket {socket_id} removed.")
        else:
            logger.error(f"Socket {socket_id} not found.")

    def register_connection(self, socket_id, username, request):
        """Register a new connection to a socket."""
        if socket_id in self.sockets:
            self.sockets[socket_id]["connections"][username] = {
                "sid_socketio": request.sid,
                "user_agent": request.headers.get("User-Agent", "N/A"),
                "ip_address": request.remote_addr,
            }
        else:
            logger.error(f"Socket {socket_id} not found.")

    def unregister_connection(self, socket_id, username):
        """Unregister a connection from a socket."""
        if socket_id in self.sockets:
            if username in self.sockets[socket_id]["connections"]:
                del self.sockets[socket_id]["connections"][username]
            else:
                logger.error(f"Connection {username} not found in socket {socket_id}.")
        else:
            logger.error(f"Socket {socket_id} not found.")

    def resolve_rooms(self, socketio):
        """Resolve the rooms for a given socket."""
        out = {}
        for namespace, data in self.sockets.items():
            out[namespace] = {}
            for username, connection in data["connections"].items():
                out[namespace][username] = {
                    "sid_socketio": connection["sid_socketio"],
                    "user_agent": connection["user_agent"],
                    "ip_address": connection["ip_address"],
                    "status": False,
                    "rooms": []
                }
                current_nsp = socketio.server.manager.rooms[namespace]
                eio_socketio = current_nsp[None][connection["sid_socketio"]]
                out[namespace][username]["eio_socketio"] = eio_socketio

                for room_name, room_data in current_nsp.items():
                    if room_name:
                        for room_sid in room_data.keys():
                            if room_sid == connection["sid_socketio"]:
                                out[namespace][username]["rooms"].append(room_name)

                eio_socket = socketio.server.eio.sockets[eio_socketio]
                out[namespace][username]["status"] = eio_socket.connected

        return out
