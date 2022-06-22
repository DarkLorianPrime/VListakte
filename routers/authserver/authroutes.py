import uuid

from fastapi import APIRouter, Form, HTTPException
from starlette.responses import JSONResponse

from libraries.database.async_database import SHAPassword, DatabaseORM

router = APIRouter()


@router.post("/api/v1/registration/")
async def registration(username: str = Form(...), password: str = Form(...)):
    db = DatabaseORM()
    if await db.entry_exists(table_name="UserAccount", where={"username": username}):
        raise HTTPException(status_code=400, detail={"error": "account already exists."})

    hashed_password = await SHAPassword("UserAccount").create_password(password)
    uuid_account = uuid.uuid4()
    await db.create_one_entry(table_name="UserAccount",
                              values={"username": username, "password": hashed_password, "token": uuid_account})
    user_id = await db.get_filtered_entries("UserAccount", {"username": username})

    await db.create_one_entry(table_name="Roles_UsersAccount", values={"role_id": 1, "user_id": user_id[0]["id"]})
    return JSONResponse(status_code=200, content={"response": str(uuid_account)})


@router.post("/api/v1/login/")
async def authorization(username: str = Form(...), password: str = Form(...)):
    db = DatabaseORM()

    if await SHAPassword("UserAccount").check_password(password=password, username=username):
        account = await db.get_filtered_entries(table_name="useraccount", where={"username": username})
        await db.disconnect()
        return JSONResponse(status_code=200, content={"response": str(account[0]["token"])})

    raise HTTPException(status_code=400, detail={"error": "account not found."})
