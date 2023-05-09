import uuid

from databases.backends.postgres import Record
from fastapi import APIRouter, Form, HTTPException, Security
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from extras.validators import is_auth
from routers.authserver.models import User, UserRoles

# HELLO!

router = APIRouter()


@router.post("/registration/", status_code=200)
async def registration(username: str = Form(...), password: str = Form(...)):
    if await User.objects().filter(User.username == username).exists():
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Username already exists")

    hashed_password = User.create_password(password)
    access_token = uuid.uuid4()
    user = await User.objects().insert("id", username=username, password=hashed_password, token=access_token)
    await UserRoles.objects().insert(role_id=1, user_id=user.id)
    return {"access_token": str(access_token)}


@router.post("/login/", status_code=200)
async def authorization(username: str = Form(...), password: str = Form(...)):
    instance = await User.valid_password(username=username, clear_password=password)

    if instance:
        return {"access_token": str(instance.token)}

    raise HTTPException(status_code=400, detail="Username or password not found")


@router.get("/get/roles/", status_code=200)
async def get_roles(user: Record = Security(is_auth)):
    roles = await UserRoles.objects().filter(UserRoles.user_id == user.id).all().values("role_id", "user_id")

    return roles


@router.get("/get/users/", status_code=200)
async def get_user():
    users = await User.objects().all().values("id", "username")
    return users
