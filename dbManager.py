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

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discord_users (
                    discord_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    mute BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            conn.commit()
            logger.info("Discord users table created or already exists.")

    def getUser(self, id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
            user_fetch = cursor.fetchone()

            cursor.execute("SELECT * FROM discord_users WHERE user_id = ?", (id,))
            discord_fetch = cursor.fetchone()
            if user_fetch:
                if discord_fetch:
                    return user.User(user_fetch[0], user_fetch[1], user_fetch[2], user_fetch[3], user_fetch[4], user_fetch[5], user_fetch[6], discord_id=discord_fetch[0], discord_mute=discord_fetch[2])
                else:
                    return user.User(user_fetch[0], user_fetch[1], user_fetch[2], user_fetch[3], user_fetch[4], user_fetch[5], user_fetch[6])
            return None

    def getAllDiscordIds(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM discord_users")
                rows = cursor.fetchall()
                return [row for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all discord ids: {e}")
            return []

    def linkDiscordId(self, discord_id, user_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO discord_users (discord_id, user_id, mute) VALUES (?, ?, ?)", (discord_id, user_id, 0))
                conn.commit()
                logger.info("Linked Discord ID %s to user ID %d.", discord_id, user_id)
                return True, ""
        except Exception as e:
            logger.error(f"Error linking Discord ID: {e}")
            return False, e

    def unlinkDiscordId(self, discord_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM discord_users WHERE discord_id = ?", (discord_id,))
                conn.commit()
                logger.info("Unlinked Discord ID %s.", discord_id)
                return True, ""
        except Exception as e:
            logger.error(f"Error unlinking Discord ID: {e}")
            return False, e

    def getUserByName(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
            user_fetch = cursor.fetchone()
            if user_fetch:
                cursor.execute("SELECT * FROM discord_users WHERE user_id = ?", (user_fetch[0],))
                discord_fetch = cursor.fetchone()

                if discord_fetch:
                    return user.User(user_fetch[0], user_fetch[1], user_fetch[2], user_fetch[3], user_fetch[4], user_fetch[5], user_fetch[6], discord_id=discord_fetch[0], discord_mute=discord_fetch[2])
                else:
                    return user.User(user_fetch[0], user_fetch[1], user_fetch[2], user_fetch[3], user_fetch[4], user_fetch[5], user_fetch[6])
            return None

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

    def getUserByDiscordID(self, discord_id):
        """
        Récupère un utilisateur par son ID Discord

        Args:
            discord_id (str): L'ID Discord de l'utilisateur

        Returns:
            User: L'objet User correspondant à l'ID Discord
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM discord_users WHERE discord_id = ?", (discord_id,))
                discord_user = cursor.fetchone()
                if discord_user:
                    user_id = discord_user[1]
                    return self.getUser(user_id)
                return None
        except Exception as e:
            logger.error(f"Error fetching user by Discord ID: {e}")
            return None

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
                cursor.execute("""
                    SELECT users.*, discord_users.discord_id, discord_users.mute
                    FROM users
                    LEFT JOIN discord_users ON users.id = discord_users.user_id
                    ORDER BY users.id
                """)
                users = []
                for row in cursor.fetchall():
                    user_fetch = user.User(
                        id=row['id'],
                        username=row['name'],
                        password=row['password'],
                        password_needs_update=bool(row['password_needs_update']),
                        is_admin=bool(row['is_admin']),
                        creation_time=row['creation_time'],
                        last_connection=row['last_connection'],
                        discord_id=row['discord_id'] if row['discord_id'] else None,
                        discord_mute=bool(row['mute'])
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

    def discordMute(self, discord_id, mute):
        """
        Update the mute status of a Discord user

        Args:
            discord_id (str): The Discord ID of the user
            mute (bool): The mute status to set

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE discord_users SET mute = ? WHERE discord_id = ?", (mute, discord_id))
                conn.commit()
                if cursor.rowcount == 0:
                    logger.warning("No Discord user found with id %s to update mute status.", discord_id)
                    return False, "No Discord user found with this ID"
                else:
                    logger.info("Mute status updated for Discord user with id %s.", discord_id)
                    return True, ""
        except Exception as e:
            logger.error(f"Error updating mute status for Discord user {discord_id}: {e}")
            return False, f"An error occurred: {e}"
