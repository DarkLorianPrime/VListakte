from datetime import datetime
from typing import Optional, Union

from databases.backends.postgres import Record
from fastapi import APIRouter, Query, Form, HTTPException, Depends
from starlette.responses import JSONResponse

from extras.validators import has_access, is_auth
from libraries.database.async_database import DatabaseORM

router = APIRouter()


@router.get("/api/v1/", dependencies=[Depends(is_auth)])
async def blog_list(offset: str = Query(0, max_length=50), limit: str = Query(-1, max_length=50)):
    db = DatabaseORM()
    blogs = await db.get_all_entries(table_name="blog")

    return JSONResponse(status_code=200,
                        content=[{k: str(v) for k, v in blog.items()} for blog in blogs[int(offset):int(limit)]])


@router.post("/api/v1/")
async def blog_create(user: Record = Depends(is_auth),
                      title: str = Form(...),
                      description: str = Form(...),
                      authors: Optional[str] = Form(None)):
    db = DatabaseORM()

    if await db.entry_exists(table_name="blog", where={"owner_id": user.id, "title": title}):
        raise HTTPException(status_code=400, detail={"error": "blog already exists."})

    time = datetime.now()
    create_data = {"owner_id": user.id, "title": title, "created_at": time, "description": description,
                   "updated_at": time}
    await db.create_one_entry(table_name="blog", values=create_data)

    blog = await db.get_filtered_entries(table_name="blog", where={"title": title, "owner_id": user.id})

    if authors:
        values = [{"blog_id": int(blog[0].id), "author_id": int(element)} for element in authors.split(", ")]
        await db.create_many_entries(table_name="blog_author", values=values)

    await db.disconnect()

    create_data = {key: str(value) for key, value in create_data.items()}
    return JSONResponse(status_code=201, content={"response": create_data})


@router.patch("/api/v1/{process_id}/", dependencies=[Depends(has_access)])
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
    params["updated_at"] = datetime.now()
    await db.update(table_name="blog", values=[params], where={"id": process_id})
    await db.delete(table_name="blog_author", where={"blog_id": process_id})

    values = [{"blog_id": int(process_id), "author_id": int(element)} for element in authors.split(", ")]
    await db.create_many_entries(table_name="blog_author", values=values)

    return JSONResponse(status_code=200, content={"response": "ok"})


@router.delete("/api/v1/{process_id}/", dependencies=[Depends(has_access)])
async def blog_delete(process_id: int):
    db = DatabaseORM()

    await db.delete(table_name="blog", where={"id": process_id})
    await db.delete(table_name="blog_author", where={"blog_id": process_id})

    return JSONResponse(status_code=200, content={"response": "ok"})
