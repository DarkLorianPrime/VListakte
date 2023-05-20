import uuid
from typing import Optional, List

from databases.backends.postgres import Record
from fastapi import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from routers.authserver.models import User, UserRoles
from routers.authserver.responses import ErrorResponses


class UserRepository:
    async def is_username_exists(self, username: str) -> bool:
        return await User.objects().filter(User.username == username).exists()

    async def create_account(self, username: str, clear_password: str) -> uuid.UUID:
        hashed_password = User.create_password(clear_password)
        access_token = uuid.uuid4()
        user = await User.objects().insert("id", username=username, password=hashed_password, token=access_token)
        await UserRoles.objects().insert(role_id=1, user_id=user.id)
        return access_token

    async def get_roles(self, user: Record) -> List[int]:
        roles = await UserRoles.objects().filter(UserRoles.user_id == user.id).all().values("role_id")
        return [role.role_id for role in roles]

    async def get_users(self) -> List[Record]:
        return await User.objects().all().values("id", "username")

    async def validate_token(self, username: str, password: str) -> uuid.UUID:
        instance = await User.valid_password(username=username, clear_password=password)
        if not instance:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=ErrorResponses.DATA_NF)

        return instance.token
