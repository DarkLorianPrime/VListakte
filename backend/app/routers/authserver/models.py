import hashlib
from datetime import datetime
from os import getenv
from typing import Self

from databases.backends.postgres import Record

from libraries.orm.core import Model
from libraries.orm.fields import SerialField, StringField, TimestampField, BooleanField, UUIDField, IntegerField


class User(Model):
    tablename = "users"
    id = SerialField()
    password = StringField(max_length=128)
    username = StringField(max_length=150)
    last_login = TimestampField(default=None)
    registration_data = TimestampField(default=datetime.now())
    is_admin = BooleanField(default=False)
    token = UUIDField()

    @classmethod
    def create_password(cls, clear_password: str) -> hex:
        security_token = getenv("SECURITY_TOKEN").encode()
        return hashlib.sha256(security_token + clear_password.encode()).hexdigest()

    @classmethod
    async def valid_password(cls, username: str, clear_password: str) -> Self:
        hashed_password = cls.create_password(clear_password)
        query = cls.objects().filter(cls.username == username, cls.password == hashed_password).first("token")
        return await query


class UserRoles(Model):
    tablename = "Roles_Users"
    id = SerialField()
    role_id = IntegerField()
    user_id = IntegerField()