import traceback
import uuid
from datetime import datetime
from typing import Optional, Union, Dict, Any

from databases.backends.postgres import Record
from fastapi import APIRouter, Query, Form, HTTPException, Depends
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, \
    HTTP_204_NO_CONTENT

from extras.validators import has_access, is_auth
from extras.values_helper import serializer
from routers.authserver.models import User
from routers.blogs.models import Blog, BlogAuthors
from routers.posts.models import Post

router = APIRouter()


@router.get("/", dependencies=[Depends(is_auth)], status_code=HTTP_200_OK)
async def blog_list(offset: str = Query(0, max_length=50), limit: str = Query(-1, max_length=50)):
    return Blog.objects().all()[int(offset):int(limit)]


@router.post("/", status_code=HTTP_201_CREATED)
async def blog_create(user: Record = Depends(is_auth),
                      title: str = Form(...),
                      description: str = Form(...),
                      authors: Optional[str] = Form(None)):
    if await Blog.objects().filter(Blog.owner_id == user.id, Blog.title == title).exists():
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Blog with this title already exists")

    time = datetime.now()
    values = {"owner_id": user.id,
              "title": title,
              "created_at": time,
              "description": description,
              "updated_at": time,
              "id": str(uuid.uuid4())}

    blog = await Blog.objects().insert("id", **values)

    if authors:
        try:
            authors_values = [{"blog_id": blog.id, "author_id": int(element)}
                              for element in authors.split(", ") if await User.filter(User.id == int(element)).exists()]
            authors = await BlogAuthors.objects().insert_many(authors_values, "author_id")
        except ValueError:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid authors format. Try again with format: 1, 2, 3")

    create_data = {key: str(value) for key, value in values.items()}
    create_data["id"] = blog.id
    if authors:
        create_data["authors_id"] = [instance.author_id for instance in authors]

    return create_data


@router.get("/{process_id}/", dependencies=[Depends(is_auth)], status_code=HTTP_200_OK)
async def blog_detail(process_id: uuid.UUID):
    blog = await Blog.filter(Blog.id == process_id).first()

    if blog is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="blog with this ID not found")

    blog_authors = await BlogAuthors.filter(BlogAuthors.blog_id == process_id).all().values("author_id")
    return {"blog": blog, "authors": blog_authors}


@router.patch("/{process_id}/", dependencies=[Depends(has_access)], response_model=None, status_code=HTTP_200_OK)
async def blog_update(process_id: uuid.UUID,
                      title: Optional[str] = Form(None),
                      description: Optional[str] = Form(None),
                      authors: Optional[str] = Form(None)) -> Union[HTTPException, Dict[str, Any]]:

    if not await Blog.filter(Blog.id == process_id).exists():
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="blog with this ID not found")

    params = {
        "updated_at": datetime.now(),
    }

    if title:
        params["title"] = title

    if description:
        params["description"] = description

    if title or description:
        await Blog.filter(Blog.id == process_id).update(params)

    if authors:
        await BlogAuthors.filter(BlogAuthors.blog_id == process_id).delete()
        values = [{"blog_id": process_id, "author_id": int(element)}
                  for element in authors.split(", ") if await User.filter(User.id == int(element)).exists()]

        await BlogAuthors.objects().insert_many(values)

    params.update(authors=authors)
    return {"status": "ok", **params}


@router.delete("/{process_id}/", dependencies=[Depends(has_access)], status_code=HTTP_204_NO_CONTENT)
async def blog_delete(process_id: uuid.UUID):
    await BlogAuthors.filter(BlogAuthors.blog_id == process_id).delete()
    await Blog.filter(Blog.id == process_id).delete()
    await Post.filter(Post.blog_id == process_id).delete()
