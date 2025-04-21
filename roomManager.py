from flask_socketio import join_room, leave_room, rooms, emit
from flask import request

class RoomManager:
    """
    Classe qui gère les rooms pour les jeux en utilisant directement
    les fonctionnalités de Flask-SocketIO.
    """

    def __init__(self, socketio):
        """
        Initialise le RoomManager avec l'instance SocketIO

        Args:
            socketio: L'instance SocketIO à utiliser
        """
        self.socketio = socketio
        self.active_rooms = set()  # Ensemble des rooms actives

    def add_player_to_room(self, room_id, username, sid=None):
        """
        Ajoute un joueur à une room spécifique

        Args:
            room_id (str): L'identifiant de la room
            username (str): Le nom d'utilisateur (pour logging)
            sid (str, optional): L'identifiant de session du joueur (utilise request.sid par défaut)

        Returns:
            bool: True si l'ajout est réussi
        """
        if sid is None:
            sid = request.sid

        join_room(room_id, sid=sid)
        self.active_rooms.add(room_id)
        print(f"[RoomManager] {username} a rejoint la room {room_id}")
        return True

    def remove_player_from_room(self, room_id, username, sid=None):
        """
        Supprime un joueur d'une room spécifique

        Args:
            room_id (str): L'identifiant de la room
            username (str): Le nom d'utilisateur (pour logging)
            sid (str, optional): L'identifiant de session du joueur (utilise request.sid par défaut)

        Returns:
            bool: True si la suppression est réussie
        """
        if sid is None:
            sid = request.sid

        leave_room(room_id, sid=sid)
        print(f"[RoomManager] {username} a quitté la room {room_id}")
        return True

    def get_player_rooms(self, sid=None):
        """
        Récupère la liste des rooms d'un joueur

        Args:
            sid (str, optional): L'identifiant de session du joueur (utilise request.sid par défaut)

        Returns:
            list: La liste des rooms auxquelles le joueur appartient
        """
        if sid is None:
            sid = request.sid

        return rooms(sid)

    def list_all_rooms(self):
        """
        Affiche dans la console toutes les rooms enregistrées dans SocketIO
        """
        all_rooms = self.socketio.server.manager.rooms
        print("[RoomManager] Liste de toutes les rooms enregistrées :")
        for namespace, rooms in all_rooms.items():
            print(f"Namespace: {namespace}")
            for room in rooms:
                print(f"  - Room: {room}")

    def get_available_rooms(self):
        """
        Récupère la liste des rooms disponibles

        Returns:
            set: Un ensemble des rooms actives
        """
        return self.active_rooms

    def broadcast_to_room(self, room_id, event, data, skip_sid=None):
        """
        Envoie un message à tous les membres d'une room

        Args:
            room_id (str): L'identifiant de la room
            event (str): Le nom de l'événement à émettre
            data (dict): Les données à envoyer
            skip_sid (str, optional): SID à ignorer pour l'émission
        """
        # ! DEBUG
        # print("-" * 60)
        # self.list_all_rooms()
        # print(f"SIDs dans room {room_id}: {self.socketio.server.manager.rooms.get('/', {}).get(f'{room_id}', [])}")
        # print("\nEVENT: ", event)
        # print("DATA: ", data)
        # print("-" * 60)
        self.socketio.emit(event, data, room=room_id, skip_sid=skip_sid)


    def clear_player_rooms(self, username, sid=None):
        """
        Supprime un joueur de toutes ses rooms

        Args:
            username (str): Le nom d'utilisateur (pour logging)
            sid (str, optional): L'identifiant de session du joueur (utilise request.sid par défaut)
        """
        if sid is None:
            sid = request.sid

        player_rooms = self.get_player_rooms(sid)
        for room in player_rooms:
            # Ne quitte pas la room par défaut de SocketIO (qui est le SID)
            if room != sid:
                self.remove_player_from_room(room, username, sid)

    def delete_room(self, room_id):
        """
        Supprime une room spécifique

        Args:
            room_id (str): L'identifiant de la room à supprimer
        """
        if room_id in self.active_rooms:
            self.active_rooms.remove(room_id)
            # Supprime tous les membres de la room dans Flask-SocketIO
            room_members = self.socketio.server.manager.rooms.get('/', {}).get(room_id, []).copy()
            for sid in room_members:
                leave_room(room_id, sid=sid)
            print(f"[RoomManager] La room {room_id} a été supprimée.")
        else:
            print(f"[RoomManager] La room {room_id} n'existe pas ou a déjà été supprimée.")
