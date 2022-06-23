from databases.backends.postgres import Record
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from extras.validators import is_auth
from extras.values_helper import serializer
from libraries.database.async_database import DatabaseORM

router = APIRouter()


@router.get("/getroles/")
async def get_roles(user: Record = Depends(is_auth)):
    roles = await DatabaseORM().get_filtered_entries(table_name="roles_users", where={"user_id": user.id})

    return JSONResponse(status_code=200, content={"response": serializer(roles, need_columns=["role_id", "user_id"])})


@router.get("/getusers/")
async def get_user():
    users = await DatabaseORM().get_all_entries(table_name="Users")
    return JSONResponse(status_code=200, content={"response": serializer(users, need_columns=["id", "username"])})
