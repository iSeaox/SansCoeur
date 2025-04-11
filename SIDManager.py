class SIDManager:
    """
    Une classe pour gérer l'association entre les SIDs (Identifiants de Sécurité) et les noms d'utilisateur.
    """

    def __init__(self):
        """Initialise un mappage vide entre les noms d'utilisateur et les SIDs."""
        self.username_to_sid = {}

    def addMapping(self, sid, username):
        """
        Ajoute un mappage entre un SID et un nom d'utilisateur.

        Args:
            sid (str): L'Identifiant de Sécurité
            username (str): Le nom d'utilisateur associé
        """
        self.username_to_sid[username] = sid

    def getUsername(self, sid):
        """
        Récupère le nom d'utilisateur associé à un SID.

        Args:
            sid (str): L'Identifiant de Sécurité

        Returns:
            str: Le nom d'utilisateur associé ou None si non trouvé
        """
        for username, stored_sid in self.username_to_sid.items():
            if stored_sid == sid:
                return username
        return None

    def getSID(self, username):
        """
        Récupère le SID associé à un nom d'utilisateur.

        Args:
            username (str): Le nom d'utilisateur

        Returns:
            str: Le SID associé ou None si non trouvé
        """
        return self.username_to_sid.get(username)

    def removeMapping(self, sid=None, username=None):
        """
        Supprime un mappage en utilisant soit le SID, soit le nom d'utilisateur.

        Args:
            sid (str, optional): Le SID à supprimer
            username (str, optional): Le nom d'utilisateur à supprimer

        Returns:
            bool: True si le mappage a été supprimé, False sinon
        """
        if username and username in self.username_to_sid:
            del self.username_to_sid[username]
            return True
        elif sid:
            for user, stored_sid in list(self.username_to_sid.items()):
                if stored_sid == sid:
                    del self.username_to_sid[user]
                    return True
        return False

    def getAllMapping(self):
        """
        Récupère tous les mappages nom d'utilisateur vers SID.

        Returns:
            dict: Un dictionnaire de tous les mappages nom d'utilisateur vers SID
        """
        return self.username_to_sid.copy()