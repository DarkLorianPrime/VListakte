from databases.backends.postgres import Record
from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import JSONResponse

from extras.validators import is_auth
from libraries.database import get_all_entries, get_database_instance, get_filtered_entries

router = APIRouter()


@router.get("/api/v1/getroles/")
async def get_roles(user: Record = Depends(is_auth)):
    db = await get_database_instance()
    roles = await get_filtered_entries(db, "roles_usersaccount", {"user_id": user.id})
    await db.disconnect()
    return JSONResponse(status_code=200, content={"response": [dict(role.items()) for role in roles]})


@router.get("/api/v1/getusers/", status_code=status.HTTP_200_OK)
async def get_user():
    db = await get_database_instance()
    users = await get_all_entries(db, "UserAccount")
    await db.disconnect()
    return {"response": users}
