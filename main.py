from fastapi import FastAPI

from libraries.database.async_database import DatabaseORM
from routers.authserver import authroutes, permissionauth
from routers.blogs import blogs
from routers.posts import posts

app = FastAPI()


@app.on_event("startup")
async def startup():
    await DatabaseORM().connect()


@app.on_event("shutdown")
async def shutdown():
    await DatabaseORM().disconnect()


app.include_router(authroutes.router)
app.include_router(permissionauth.router)
app.include_router(blogs.router)
app.include_router(posts.router)
