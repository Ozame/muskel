import uuid
from typing import List

import mongoengine as me

import model as mo
import security


def create_role(role_name: str) -> mo.Role:
    role = mo.Role.objects(name=role_name)
    if role.count() == 0:
        role = mo.Role(uuid=uuid.uuid4(), name=role_name)
        try:
            role.save()
        except (me.NotUniqueError, me.ValidationError):
            return None
    else:
        return role.get()


def create_user(username: str, password: str, roles: List[mo.Role] = None) -> mo.User:
    id = uuid.uuid4()
    hashed_password = security.hash_password(password, id.bytes)
    user = mo.User(username=username, password=hashed_password, uuid=id)
    user_role = mo.Role.objects(name="USER").get()
    user.roles = roles
    if not user_role in user.roles or not roles:
        user.roles.append(user_role)
    try:
        user.save()
    except (me.NotUniqueError, me.ValidationError):
        return None
    return user
