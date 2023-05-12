import uuid
from datetime import datetime
from typing import Dict, Any, List, Set

from databases.backends.postgres import Record
from fastapi import APIRouter, Query, HTTPException, Depends
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, \
    HTTP_204_NO_CONTENT

from extras.validators import has_access, is_auth
from routers.blogs.pydantic_models import BlogPatchModel, BlogInsertModel, BlogPatchResponseModel, \
    RetrieveResponseModel, BlogRetrieveResponseModel, CreateResponseModel
from routers.blogs.repositories import BlogRepository, BlogAuthorsRepository
from routers.blogs.responses import ErrorResponses

router = APIRouter()
err_response = ErrorResponses


@router.get("/",
            dependencies=[Depends(is_auth)],
            status_code=HTTP_200_OK,
            response_model=List[BlogRetrieveResponseModel])
async def blog_list(offset: str = Query(0, max_length=50), limit: str = Query(-1, max_length=50),
                    repository: BlogRepository = Depends(BlogRepository)):
    return await repository.get_all_blogs(int(offset), int(limit))


@router.post("/", status_code=HTTP_201_CREATED, response_model=CreateResponseModel)
async def blog_create(user: Record = Depends(is_auth),
                      blog: BlogInsertModel = Depends(BlogInsertModel.to_form),
                      repository: BlogRepository = Depends(BlogRepository)):
    if await repository.check_blog_exists_title(title=blog.title, user=user):
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=err_response.TITLE_EXISTS)

    time = datetime.now()
    dict_blog = blog.dict(exclude_unset=True)
    blog_id = uuid.uuid4()
    dict_blog.update({
        "owner_id": user.id,
        "created_at": time,
        "updated_at": time,
        "id": blog_id
    })

    await repository.create_blog(dict_blog)

    if "authors" in dict_blog:
        try:
            await repository.delete_authors(blog_id)
            authors_set = set(map(int, dict_blog["authors"].split(",")))
            ids: List[Record] | List = await repository.insert_authors(blog_id=blog_id, users=authors_set)
            dict_blog["authors"] = [author.author_id for author in ids]
        except ValueError:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=err_response.INVALID_AUTHORS)

    return dict_blog


@router.get("/{process_id}/",
            dependencies=[Depends(is_auth)],
            status_code=HTTP_200_OK,
            response_model=RetrieveResponseModel)
async def blog_detail(process_id: uuid.UUID,
                      repository: BlogRepository = Depends(BlogRepository),
                      authors_repository: BlogAuthorsRepository = Depends(BlogAuthorsRepository)):
    blog: Record | None = await repository.get_one_blog_by_id(process_id)

    if blog is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=err_response.ID_NOT_FOUND)

    blog_authors: List[int] = await authors_repository.get_blog_authors_ids(process_id)
    return {"blog": blog, "authors": blog_authors}


@router.patch("/{process_id}/",
              dependencies=[Depends(has_access)],
              status_code=HTTP_200_OK,
              response_model=BlogPatchResponseModel)
async def blog_update(process_id: uuid.UUID,
                      blog: BlogPatchModel = Depends(BlogPatchModel.to_form),
                      repository: BlogRepository = Depends(BlogRepository)):
    if not await repository.check_blog_exists_by_id(blog_id=process_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=err_response.ID_NOT_FOUND)

    dict_blog: Dict[str, Any] = blog.dict(exclude_unset=True)
    dict_blog["updated_at"] = datetime.now()

    if "title" in dict_blog or "description" in dict_blog:
        await repository.update_blog(process_id, dict_blog)

    if "authors" in dict_blog:
        try:
            await repository.delete_authors(process_id)
            authors_set: Set[int] = set(map(int, dict_blog["authors"].split(",")))
            ids: List[Record] | List = await repository.insert_authors(blog_id=process_id, users=authors_set)

            dict_blog["authors"] = [author["author_id"] for author in ids]
        except ValueError:
            raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=err_response.INVALID_AUTHORS)

    return {"status": "ok", **dict_blog}


@router.delete("/{process_id}/",
               dependencies=[Depends(has_access)],
               response_model=None,
               status_code=HTTP_204_NO_CONTENT)
async def blog_delete(process_id: uuid.UUID,
                      repository: BlogRepository = Depends(BlogRepository)):
    await repository.delete_blog(process_id)
