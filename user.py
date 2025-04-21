from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password, password_needs_update):
        self.id = id
        self.username = username
        self.password = password
        self.password_needs_update = password_needs_update