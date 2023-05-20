from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from libraries.orm.database import db
from routers.authserver import routers
from routers.blogs import blogs
from routers.posts import posts


async def startup():
    await db.connect()


async def shutdown():
    await db.connect()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await db.connect()
#     yield
#     await db.disconnect()

app = FastAPI()
router = APIRouter(prefix="/api/v1")


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "Error": "Name field is missing"}),
    )


router.include_router(router=routers.router)
router.include_router(router=blogs.router)
router.include_router(router=posts.router)
app.include_router(router=router)
