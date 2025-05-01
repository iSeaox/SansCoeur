import sqlite3
import logging
import os
logger = logging.getLogger(f"app.{__name__}")

import user

class dbManager:
    def __init__(self, path):
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        self.db_path = path
        logger.info("Database path set to %s", self.db_path)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                password_needs_update BOOLEAN NOT NULL DEFAULT 0,
                is_admin BOOLEAN NOT NULL DEFAULT 0,
                creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_connection DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Users table created or already exists.")

    def getUser(self, id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
            user_fetch = cursor.fetchone()
            if user_fetch:
                return user.User(user_fetch[0], user_fetch[1], user_fetch[2], user_fetch[3], user_fetch[4], user_fetch[5], user_fetch[6])
            return None

    def getUserByName(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
            user_fetch = cursor.fetchone()
            if user_fetch:
                return user.User(user_fetch[0], user_fetch[1], user_fetch[2], user_fetch[3], user_fetch[4], user_fetch[5], user_fetch[6])
            return None

    def updatePassword(self, id, new_password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = ?, password_needs_update = 0 WHERE id = ?", (new_password, id))
            if cursor.rowcount == 0:
                logger.warning("No user found with id %d to update the password.", id)
                return (False, "Vous n'existez pas dans la base de données.")
            else:
                conn.commit()
                logger.info("Password updated for user with id %d.", id)
                return (True, "Votre mot de passe a été mis à jour avec succès.")

    def insertUser(self, name, password, should_update_password):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if self.getUserByName(name):
                logger.warning("User %s already exists in the database.", name)
                return False, "User already exists."
            cursor.execute("INSERT INTO users (name, password, password_needs_update) VALUES (?, ?, ?)", (name, password, should_update_password))
            conn.commit()
            logger.info("User %s inserted into the database.", name)
            return True, ""

    def updateUserPassword(self, username, password_hash):
        """
        Updates a user's password in the database.

        Args:
            username (str): The username of the user whose password should be updated
            password_hash (str): The new password hash to store

        Returns:
            bool: True if the update was successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE users SET password = ? WHERE name = ?",
                    (password_hash, username)
                )
                if cursor.rowcount == 0:
                    logger.warning("No user found with username %s to update the password.", username)
                    return False
                logger.info("Password updated for user %s.", username)
                return True
        except Exception as e:
            logger.error(f"Error updating user password: {e}")
            return False

    def updateUserPasswordFlag(self, username, should_update_password):
        """
        Updates a user's password change flag in the database.

        Args:
            username (str): The username of the user whose flag should be updated
            should_update_password (int): 1 if the user should change their password on next login, 0 otherwise

        Returns:
            bool: True if the update was successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE users SET password_needs_update = ? WHERE name = ?",
                    (should_update_password, username)
                )
                if cursor.rowcount == 0:
                    logger.warning("No user found with username %s to update the password flag.", username)
                    return False, f"No user with username '{username}' found"
                logger.info("Password flag updated for user %s.", username)
                return True, ""
        except Exception as e:
            logger.error(f"Error updating user password flag: {e}")
            return False, f"An error occurred: {e}"

    def getAllUsers(self):
        """
        Récupère tous les utilisateurs de la base de données

        Returns:
            list: Liste des objets User
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users ORDER BY id")

                users = []
                for row in cursor.fetchall():
                    user_fetch = user.User(
                        id=row['id'],
                        username=row['name'],
                        password=row['password'],
                        password_needs_update=bool(row['password_needs_update']),
                        is_admin=bool(row['is_admin']),
                        creation_time=row['creation_time'],
                        last_connection=row['last_connection']
                    )
                    users.append(user_fetch)
                return users
        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            return []

    def deleteUser(self, username):
        """
        Delete a user from the database by username

        Args:
            username (str): The username of the user to delete

        Returns:
            bool: True if successful, raises an exception otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM users WHERE name = ?", (username,))
                connection.commit()
                if cursor.rowcount == 0:
                    return False, f"No user with username '{username}' found"
                return True, ""
        except sqlite3.Error as e:
            return False, f"An error occurred: {e}"

    def updateLoginTime(self, user_id, login_time):
        """
        Update the last connection time for a user

        Args:
            user_id (int): The ID of the user
            login_time (datetime): The datetime of the login

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET last_connection = ? WHERE id = ?",
                              (login_time.strftime('%Y-%m-%d %H:%M:%S'), user_id))
                conn.commit()
                if cursor.rowcount == 0:
                    logger.warning("No user found with id %d to update login time.", user_id)
                    return False
                else:
                    logger.info("Login time updated for user with id %d.", user_id)
                    return True
        except Exception as e:
            logger.error(f"Error updating login time for user {user_id}: {e}")
            return False
