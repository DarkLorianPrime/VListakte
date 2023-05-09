from datetime import datetime
from typing import Optional, Union

from databases.backends.postgres import Record
from fastapi import APIRouter, Query, Form, HTTPException, Depends
from starlette.responses import JSONResponse

from extras.validators import has_access, is_auth
from extras.values_helper import serializer
from routers.blogs.models import Blog, BlogAuthors

router = APIRouter()


@router.get("/", dependencies=[Depends(is_auth)], status_code=200)
async def blog_list(offset: str = Query(0, max_length=50), limit: str = Query(-1, max_length=50)):
    return await Blog.objects().all()[int(offset):int(limit)]


@router.post("/", status_code=201)
async def blog_create(user: Record = Depends(is_auth),
                      title: str = Form(...),
                      description: str = Form(...),
                      authors: Optional[str] = Form(None)):
    if await Blog.objects().filter(Blog.owner_id == user.id, Blog.title == title).exists():
        raise HTTPException(status_code=400, detail="blog already exists.")

    time = datetime.now()
    values = {"owner_id": user.id, "title": title, "created_at": time, "description": description, "updated_at": time}
    blog = await Blog.objects().insert("id", **values)

    if authors:
        values = [{"blog_id": int(blog.id), "author_id": int(element)} for element in authors.split(", ")]
        await BlogAuthors.objects().insert_many(values)

    create_data = {key: str(value) for key, value in values.items()}
    return create_data


@router.get("/{process_id}/", dependencies=[Depends(is_auth)], status_code=200)
async def blog_detail(process_id: int):
    blog = await Blog.filter(Blog.id == process_id).first()
    blog_authors = await BlogAuthors.filter(BlogAuthors.blog_id == process_id).all().values("author_id")

    return {"blog": blog, "authors": blog_authors}


@router.patch("/{process_id}/", dependencies=[Depends(has_access)], response_model=None)
async def blog_update(process_id: int,
                      title: Optional[str] = Form(None),
                      description: Optional[str] = Form(None),
                      authors: Optional[str] = Form(None)) -> Union[HTTPException, JSONResponse]:
    params = {}

    if title:
        params["title"] = title

    if description:
        params["description"] = description
    date = datetime.now()
    params["updated_at"] = date
    if params:
        await db.update(table_name="blogs", values=[params], where={"id": process_id})

    if authors:

        await db.delete(table_name="blog_authors", where={"blog_id": process_id})
        values = [{"blog_id": int(process_id), "author_id": int(element)} for element in authors.split(", ") if
                  await DatabaseORM().entry_exists(table_name="users", where={"id": int(element)})]

        await db.create_many_entries(table_name="blog_authors", values=values)

    params["updated_at"] = str(date)

    # return JSONResponse(status_code=200, content={"response": "ok", "data": params})
    return {"d": "a"}


@router.delete("/{process_id}/", dependencies=[Depends(has_access)], status_code=204)
async def blog_delete(process_id: int):
    await Blog.filter(Blog.id == process_id).delete()
    await BlogAuthors.filter(BlogAuthors.blog_id == process_id).delete()
    await db.delete(table_name="posts", where={"blog_id": process_id})

    return JSONResponse(status_code=200, content={"response": "ok"})
