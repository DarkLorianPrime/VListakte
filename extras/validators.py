from typing import Optional

from fastapi import HTTPException, Header
from starlette.requests import Request

from libraries.database.async_database import DatabaseORM


async def has_access(request: Request, process_id: Optional[int], raise_exception: bool = True) -> bool:
    user = await is_auth(request.headers.get("authorization"))
    db = DatabaseORM()
    if await db.entry_exists(table_name="blogs", where={"owner_id": user.id, "id": process_id}):
        return user
    if await db.entry_exists(table_name="roles_users", where={"user_id": user.id, "role_id": 2}):
        return user
    if raise_exception:
        raise HTTPException(status_code=400, detail={
            "error": "You do not have permission to interact with this blog, or the blog does not exists."})
    return False


async def is_auth(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail={"error": "get token for headers"})

    token = authorization.split(" ")
    if len(token) != 2:
        raise HTTPException(status_code=401, detail={"error": "get token for headers"})

    account = await DatabaseORM().get_filtered_entries(table_name="Users", where={"token": token[1]})

    if not account:
        raise HTTPException(status_code=401, detail={"error": "Account with this token does not exists"})

    return account[0]
