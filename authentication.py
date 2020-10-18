"""Handles the authentication of users"""
from mongoengine.errors import DoesNotExist
import model as mo

# User loader for test purposes
# user_loader = lambda payload: {'username': payload}

def user_loader(payload):
    """Loads the user matching the payload from the database"""
    print(payload)
    username = payload['user']['username']
    try:
        user = mo.User.objects(username=username)
    except DoesNotExist:
        print(f"user with username {username} doesn't exist!")
        return None
    return user
    
def authenticate_user(username, password):
    try:
        user = mo.User.objects(username=username).get()
    except DoesNotExist:
        return None
    if user.password == password:
        return user
    else:
        return None

def hash_password(password):

    # TODO: Salt 'n' peppa
    return password

def create_user(username, password, roles=None):
    hashed_password=hash_password(password)
    user = mo.User(username=username, password=hashed_password)
    pass

