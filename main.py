from fastapi import FastAPI, APIRouter

from libraries.database.async_database import DatabaseORM
from routers.authserver import authroutes, permissionauth
from routers.blogs import blogs
from routers.posts import posts

app = FastAPI()
router = APIRouter(prefix="/api/v1")


@app.on_event("startup")
async def startup():
    await DatabaseORM().connect()


@app.on_event("shutdown")
async def shutdown():
    await DatabaseORM().disconnect()


router.include_router(router=authroutes.router)
router.include_router(router=permissionauth.router)
router.include_router(router=blogs.router)
router.include_router(router=posts.router)
app.include_router(router=router)
