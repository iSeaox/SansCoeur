import functools
from flask import render_template, request
from flask_login import current_user
from flask_socketio import disconnect, emit

import logging
logger = logging.getLogger(f"app.{__name__}")

def socketio_login_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

def socketio_admin_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            logger.warning(f"User {current_user.username if hasattr(current_user, "username") else "Unknown"} tried to access admin namespace")
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

def admin_required(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if getattr(current_user, "is_admin", None) is not None and getattr(current_user, "username", None) is not None:
            if not current_user.is_authenticated or not current_user.is_admin:
                return render_template("errors/403.html",
                                    message="Où comptez-vous aller comme ça ?",
                                    errcode=1,
                                    username=current_user.username)
            else:
                return f(*args, **kwargs)
        else:
            return render_template("errors/403.html",
                            message="Où comptez-vous aller comme ça ?",
                            errcode=2,
                            username="Unknown")
    return wrapped