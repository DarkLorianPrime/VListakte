import json
from datetime import datetime
from typing import Optional, Union

from databases.backends.postgres import Record
from fastapi import APIRouter, Query, Form, HTTPException, Depends
from starlette.responses import JSONResponse

from extras.validators import has_access, is_auth
from extras.values_helper import serializer
from libraries.database.async_database import DatabaseORM

router = APIRouter()


@router.get("/", dependencies=[Depends(is_auth)])
async def blog_list(offset: str = Query(0, max_length=50), limit: str = Query(-1, max_length=50)):
    blogs = await DatabaseORM().get_all_entries(table_name="blogs")

    return JSONResponse(status_code=200, content=serializer(blogs, offset=int(offset), limit=int(limit)))


@router.post("/")
async def blog_create(user: Record = Depends(is_auth),
                      title: str = Form(...),
                      description: str = Form(...),
                      authors: Optional[str] = Form(None)):
    db = DatabaseORM()

    if await db.entry_exists(table_name="blogs", where={"owner_id": user.id, "title": title}):
        raise HTTPException(status_code=400, detail={"error": "blog already exists."})

    time = datetime.now()
    create_data = {"owner_id": user.id, "title": title, "created_at": time, "description": description,
                   "updated_at": time}
    await db.create_one_entry(table_name="blogs", values=create_data)

    blog = await db.get_filtered_entries(table_name="blogs", where={"title": title, "owner_id": user.id})

    if authors:
        values = [{"blog_id": int(blog[0].id), "author_id": int(element)} for element in authors.split(", ")]
        await db.create_many_entries(table_name="blog_authors", values=values)

    create_data = {key: str(value) for key, value in create_data.items()}
    return JSONResponse(status_code=201, content={"response": create_data})


@router.get("/{process_id}/", dependencies=[Depends(is_auth)])
async def blog_detail(process_id: int):
    db = DatabaseORM()
    blog = await db.get_filtered_entries(table_name="blogs", where={"id": process_id})

    blog_authors = await db.get_filtered_entries(table_name="blog_authors", where={"blog_id": process_id})

    blog_values = serializer(blog)
    blog_authors = serializer(blog_authors, need_columns=["author_id"])

    return JSONResponse(status_code=200, content={"response": {"blog": blog_values, "authors": blog_authors}})


@router.patch("/{process_id}/", dependencies=[Depends(has_access)])
async def blog_update(process_id: int,
                      title: Optional[str] = Form(None),
                      description: Optional[str] = Form(None),
                      authors: Optional[str] = Form(None)) -> Union[HTTPException, JSONResponse]:
    db = DatabaseORM()
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

    return JSONResponse(status_code=200, content={"response": "ok", "data": params})


@router.delete("/{process_id}/", dependencies=[Depends(has_access)])
async def blog_delete(process_id: int):
    db = DatabaseORM()

    await db.delete(table_name="posts", where={"blog_id": process_id})
    await db.delete(table_name="blog_authors", where={"blog_id": process_id})
    await db.delete(table_name="blogs", where={"id": process_id})

    return JSONResponse(status_code=200, content={"response": "ok"})
