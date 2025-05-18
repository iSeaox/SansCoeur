from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password, password_needs_update, is_admin, creation_time, last_connection, discord_id=None, discord_mute=False):
        self.id = id
        self.username = username
        self.password = password
        self.password_needs_update = password_needs_update
        self.is_admin = is_admin
        self.creation_time = creation_time
        self.last_connection = last_connection
        self.discord_id = discord_id
        self.discord_mute = discord_mute