import uuid
from typing import List, Dict

from databases.backends.postgres import Record
from fastapi import APIRouter, Security, Depends, HTTPException
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY

from extras.validators import is_auth
from routers.authserver.pydantic_models import TokenResponseModel, TokenModel, RolesResponseModel, UsersResponseModel
from routers.authserver.repositories import UserRepository
from routers.authserver.responses import ErrorResponses


router = APIRouter()
err_resp = ErrorResponses()


@router.post("/registration/",
             status_code=HTTP_201_CREATED,
             response_model=TokenResponseModel)
async def registration(token: TokenModel = Depends(TokenModel.to_form),
                       repository: UserRepository = Depends(UserRepository)):
    if await repository.is_username_exists(token.username):
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=err_resp.USERNAME_EXISTS)

    access_token: uuid.UUID = await repository.create_account(username=token.username, clear_password=token.password)
    return {"access_token": access_token}


@router.post("/login/",
             status_code=HTTP_200_OK,
             response_model=TokenResponseModel)
async def authorization(token: TokenModel = Depends(TokenModel.to_form),
                        repository: UserRepository = Depends(UserRepository)):
    token: uuid.UUID = await repository.validate_token(username=token.username, password=token.password)
    return {"access_token": token}


@router.get("/get/roles/",
            status_code=HTTP_200_OK,
            response_model=RolesResponseModel)
async def get_roles(user: Record = Security(is_auth),
                    repository: UserRepository = Depends(UserRepository)):
    return {"roles_ids": await repository.get_roles(user=user)}


@router.get("/get/users/",
            status_code=HTTP_200_OK,
            response_model=List[UsersResponseModel])
async def get_user(repository: UserRepository = Depends(UserRepository)):
    return await repository.get_users()
