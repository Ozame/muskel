"""Handles the authentication of users"""
import hashlib
from hmac import compare_digest

from mongoengine.errors import DoesNotExist

import model as mo

# User loader for test purposes
# user_loader = lambda payload: {'username': payload}


def user_loader(payload) -> mo.User:
    """Loads the user matching the payload from the database"""
    username = payload["user"]["username"]
    try:
        user = mo.User.objects(username=username)
    except DoesNotExist:
        print(f"user with username {username} doesn't exist!")
        return None
    return user


def authenticate_user(username: str, password: str) -> mo.User:
    try:
        user = mo.User.objects(username=username).get()
    except DoesNotExist:
        return None
    if check_user_password(user, password):
        return user
    else:
        return None


def hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 5000)


def check_password(password: bytes, password_candidate: bytes) -> bool:
    return compare_digest(password, password_candidate)


def check_user_password(user: mo.User, password_candidate: str) -> bool:
    hashed_password_candidate = hash_password(password_candidate, user.uuid.bytes)
    return check_password(user.password, hashed_password_candidate)
