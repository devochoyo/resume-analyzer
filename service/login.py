# Admin login. The username and password come from the .env file.
import os
from functools import wraps
from hmac import compare_digest

from flask import redirect, session, url_for


def check_login(username, password):
    """Return True only when the username and password match the .env values."""
    real_username = os.getenv("ADMIN_USERNAME")
    real_password = os.getenv("ADMIN_PASSWORD")

    # If the .env values are missing, nobody can log in.
    if not real_username or not real_password:
        return False

    username_ok = compare_digest(username.strip().encode(), real_username.encode())
    password_ok = compare_digest(password.encode(), real_password.encode())
    return username_ok and password_ok


def log_in():
    session["is_admin"] = True


def log_out():
    session.pop("is_admin", None)


def is_logged_in():
    return session.get("is_admin") is True


def admin_only(page):
    """Put @admin_only under a route to block people who are not logged in."""
    @wraps(page)
    def wrapper(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("main.admin_login"))
        return page(*args, **kwargs)
    return wrapper
