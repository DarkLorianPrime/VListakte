from datetime import datetime
from typing import Optional, List

from databases.backends.postgres import Record
from fastapi import APIRouter, Depends, Form, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from extras.validators import is_auth, has_access
from extras.values_helper import serializator
from libraries.database.async_database import DatabaseORM

router = APIRouter()


@router.get("/api/v1/{blog_id}/posts/")
async def get_all_posts(request: Request, blog_id: int, user: Record = Depends(is_auth), published: bool = True):
    db = DatabaseORM()
    return_dict = {"is_access": False, "posts": []}
    where_dict = {"blog_id": blog_id, "is_published": True}
    if await has_access(request=request, process_id=blog_id, raise_exception=False):
        if not published:
            where_dict["is_published"] = False
        return_dict["is_access"] = True

    posts = await db.get_filtered_entries(table_name="posts", where=where_dict)

    for post in [post for post in posts]:
        post_data = post.items()

        where = {"post_id": dict(post_data)["id"], "user_id": user.id}
        posts_likes = await db.entry_exists(table_name="post_likes", where=where)
        posts_views = await db.entry_exists(table_name="post_views", where=where)

        temp_dict = serializator([post])
        temp_dict[0]["is_liked"] = posts_likes
        temp_dict[0]["is_viewed"] = posts_views
        return_dict["posts"].append(temp_dict)

    return JSONResponse(status_code=200, content=return_dict)


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


@router.delete("/api/v1/{process_id}/posts/{post_id}/", dependencies=[Depends(has_access)])
async def delete_post(process_id: int, post_id: int):
    db = DatabaseORM()

    await db.delete(table_name="posts", where={"id": post_id, "blog_id": process_id})
    await db.delete(table_name="post_views", where={"post_id": post_id})
    await db.delete(table_name="post_likes", where={"post_id": post_id})
    await db.delete(table_name="post_commentaries", where={"post_id": post_id})

    return JSONResponse(status_code=200, content={"response": "ok"})


@router.patch("/api/v1/{process_id}/posts/{post_id}/", dependencies=[Depends(has_access)])
async def update_post(process_id: int,
                      post_id: int,
                      title: Optional[str] = Form(None),
                      text: Optional[str] = Form(None),
                      is_published: Optional[bool] = Form(None)):
    params = {}
    if title:
        params["title"] = title

    if text:
        params["text"] = text

    if is_published is not None:
        params["is_published"] = is_published

    if params:
        await DatabaseORM().update(table_name="posts", values=[params], where={"id": post_id, "blog_id": process_id})

    return JSONResponse(status_code=200, content={"response": "ok", "data": params})


@router.get("/api/v1/{process_id}/posts/{post_id}/")
async def get_one_post(request: Request, process_id: int, post_id: int, user: Record = Depends(is_auth)):
    db = DatabaseORM()
    returned_values = {"is_access": False}
    where_dict = {"is_published": True, "id": post_id}

    if not await db.entry_exists(table_name="post_views", where={"post_id": post_id, "user_id": user.id}):
        await db.create_one_entry(table_name="post_views", values={"post_id": post_id, "user_id": user.id})

    posts_likes = await db.entry_exists(table_name="post_likes", where={"post_id": post_id, "user_id": user.id})

    if await has_access(request=request, process_id=process_id, raise_exception=False):
        where_dict.pop("is_published")
        returned_values["is_access"] = True

    posts = await db.get_filtered_entries(table_name="posts", where=where_dict)

    returned_values["is_liked"] = posts_likes
    returned_values["post"] = serializator(posts)

    return JSONResponse(status_code=200, content={"response": returned_values})


@router.post("/api/v1/{process_id}/posts/{post_id}/like")
async def post_like(process_id: int, post_id: int, user: Record = Depends(is_auth)):
    db = DatabaseORM()

    if not await db.entry_exists(table_name="posts", where={"id": post_id, "blog_id": process_id}):
        raise HTTPException(status_code=404, detail={"error": "Post not found."})

    if not await db.entry_exists(table_name="post_likes", where={"post_id": post_id, "user_id": user.id}):
        await db.create_one_entry(table_name="post_likes", values={"post_id": post_id, "user_id": user.id})
        return JSONResponse(status_code=200, content={"response": "ok"})

    await db.delete(table_name="post_likes", where={"post_id": post_id, "user_id": user.id})
    return JSONResponse(status_code=200, content={"response": "ok"})


@router.get("/api/v1/posts/last/", dependencies=[Depends(is_auth)])
async def post_last():
    db = DatabaseORM()
    posts = await db.get_filtered_entries(table_name="posts", order_by="created_at desc")

    returned_dict = serializator(posts, limit=5)
    return JSONResponse(status_code=200, content={"response": returned_dict})
