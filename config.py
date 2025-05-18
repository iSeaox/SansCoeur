import os

VERSION = "0.0.2"

SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)
MANIFEST_JSON = f"manifest/manifest.json"
MANIFEST_PUBLIC_PATH = "manifest.json"

SESSION_COOKIE_NAME = 'flask_socketio_session'

DATABASE_PATH = 'instance/db.sqlite'

# ! DEBUG
DEBUG_MODE = 0
DEBUG_MODE_PLAYERS = 0
DEBUG_MODE_TALKS = 0
DEBUG_MODE_TABLE_CARDS = 0
DEBUG_MODE_END_GAME = 0
DEBUG_MODE_FAKE_ROUNDS= 0
DEBUG_MODE_FAKE_BELOTE = -1