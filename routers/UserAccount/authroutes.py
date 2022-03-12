import uuid

from fastapi import APIRouter, Form
from pydantic import BaseModel
from starlette.requests import Request

from libraries.database import SHAPassword, entry_exists, get_database_instance, create_one_entry, get_filtered_entries

router = APIRouter()


@router.post("/registration/", )
async def registration(username: str = Form(...), password: str = Form(...)):
    db = await get_database_instance()
    if await entry_exists(db, "UserAccount", {"username": username}):
        return {"error": "account already exists"}
    hashed_password = await SHAPassword().create_password(password)
    uuid_account = uuid.uuid4().hex
    await create_one_entry(db, "UserAccount",
                           {"username": username, "password": hashed_password, "token": uuid_account})
    return {"response": uuid_account}


@router.post("/login/")
async def authorization(username: str = Form(...), password: str = Form(...)):
    db = await get_database_instance()
    if await SHAPassword().check_password(db, password, username):
        account = await get_filtered_entries(db, "useraccount", {"username": username})
        return {"response": account[0]["token"]}
    return {"error": "account not registered."}