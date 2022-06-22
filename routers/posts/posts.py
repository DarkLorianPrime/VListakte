from datetime import datetime

from databases.backends.postgres import Record
from fastapi import APIRouter, Depends, Form, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from extras.validators import is_auth, has_access
from libraries.database.async_database import DatabaseORM

router = APIRouter()


@router.get("/api/v1/{blog_id}/posts/", dependencies=[Depends(is_auth)])
async def get_all_posts(request: Request, blog_id: int, published: bool = True):
    db = DatabaseORM()
    where_dict = {"blog_id": blog_id, "is_published": True}
    if not published:
        if not await has_access(request=request, process_id=blog_id, raise_exception=False):
            where_dict["is_published"] = False
    posts = await db.get_filtered_entries(table_name="posts", where=where_dict)

    return JSONResponse(status_code=200, content=[{k: str(v) for k, v in post.items()} for post in posts])


@router.post("/api/v1/{process_id}/posts/")
async def create_post(process_id: int,
                      user: Record = Depends(has_access),
                      title: str = Form(...),
                      text: str = Form(...),
                      is_published: bool = Form(...)):
    db = DatabaseORM()
    post = await db.get_filtered_entries(table_name="posts", where={"blog_id": process_id, "title": title})

    if post:
        raise HTTPException(status_code=400, detail="Post with this title already exists.")

    values = {"title": title, "text": text, "is_published": is_published, "created_at": datetime.now(),
              "author_id": user.id, "blog_id": process_id}
    await db.create_one_entry(table_name="posts", values=values)

    return JSONResponse(status_code=200, content={key: str(value) for key, value in values.items()})


@router.delete("/api/v1/{process_id}/posts/{post_id}", dependencies=[Depends(has_access)])
async def delete_post(process_id: int, post_id: int):
    db = DatabaseORM()

    await db.delete(table_name="post", where={"id": post_id, "blog_id": process_id})
    await db.delete(table_name="post_views", where={"post_id": post_id})
    await db.delete(table_name="post_likes", where={"post_id": post_id})
    await db.delete(table_name="post_commentaries", where={"post_id": post_id})

    return JSONResponse(status_code=200, content={"response": "ok"})
