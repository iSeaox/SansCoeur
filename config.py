import os

SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)

SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite"
SESSION_COOKIE_NAME = 'flask_socketio_session'