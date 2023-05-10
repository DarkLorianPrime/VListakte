from fastapi import FastAPI, APIRouter

from routers.authserver import routers
from routers.blogs import blogs
from routers.posts import posts

app = FastAPI()
router = APIRouter(prefix="/api/v1")


router.include_router(router=routers.router)
router.include_router(router=blogs.router)
# router.include_router(router=posts.router)
app.include_router(router=router)
