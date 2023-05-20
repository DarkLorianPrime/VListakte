import uuid
from datetime import datetime

from databases.backends.postgres import Record
from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_204_NO_CONTENT, \
    HTTP_201_CREATED

from extras.validators import is_auth, has_access
from routers.blogs.pydantic_models import PostsFilterModel, UpdatePostModel
from routers.posts.models import PostLike, PostView
from routers.posts.pydantic_models import CreatePostModel
from routers.posts.repositories import PostRepository, ViewRepository, LikeRepository
from routers.posts.responses import ErrorResponses

router = APIRouter()
err_resp = ErrorResponses


@router.get("/{blog_id}/posts/")
async def get_all_posts(request: Request,
                        blog_id: uuid.UUID,
                        filters: PostsFilterModel,
                        user: Record = Depends(is_auth),
                        post_repository: PostRepository = Depends(PostRepository)):
    access = await has_access(request=request, blog_id=blog_id, raise_exception=False)
    return_dict = {"has_access": bool(access), "posts": []}
    filters = filters.dict()
    published = filters.pop("published") if access else True
    posts_ids, posts = post_repository.get_posts_include_ids(**filters, published=published, blog_id=blog_id)

    likes_ids = post_repository.get_model_items(PostLike, posts_ids, user.id)
    all_likes = await post_repository.get_grouped_param_count(PostLike)

    views_ids = post_repository.get_model_items(PostView, posts_ids, user.id)
    all_views = await post_repository.get_grouped_param_count(PostView)

    for post in posts:
        dict_post = dict(post)

        dict_post["is_liked"] = post.id in likes_ids
        dict_post["is_viewed"] = post.id in views_ids

        dict_post["likes"] = await post_repository.get_count_from_grouped(post_id=post.id, result=all_likes)
        dict_post["views"] = await post_repository.get_count_from_grouped(post_id=post.id, result=all_views)

        return_dict["posts"].append(dict_post)

    return return_dict


@router.post("/{blog_id}/posts/",
             status_code=HTTP_201_CREATED,
             )
async def create_post(blog_id: uuid.UUID,
                      user: Record = Depends(has_access),
                      post: CreatePostModel = Depends(CreatePostModel.to_form),
                      repository: PostRepository = Depends(PostRepository)):
    if await repository.check_post_exists_title(blog_id=blog_id, title=post.title):
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail=err_resp.TITLE_EXISTS)

    dict_post: dict = post.dict()
    dict_post.update({
        "created_at": datetime.now(),
        "author_id": user.id,
        "blog_id": blog_id
    })

    await repository.create_post(dict_post)
    return dict_post


@router.delete("/{blog_id}/posts/{post_id}/",
               dependencies=[Depends(has_access)],
               status_code=HTTP_204_NO_CONTENT)
async def delete_post(blog_id: uuid.UUID,
                      post_id: int,
                      repository: PostRepository = Depends(PostRepository)):
    await repository.delete_post(post_id=post_id, blog_id=blog_id)


@router.patch("/{blog_id}/posts/{post_id}/",
              dependencies=[Depends(has_access)],
              status_code=HTTP_200_OK)
async def update_post(blog_id: uuid.UUID,
                      post_id: int,
                      filters: UpdatePostModel = Depends(UpdatePostModel.to_form),
                      repository: PostRepository = Depends(PostRepository)):
    filters = filters.dict(exclude_unset=True)

    if filters:
        await repository.update_post(blog_id=blog_id, post_id=post_id, parameters=filters)

    return {"status": "ok", **filters}


@router.get("/{blog_id}/posts/{post_id}/",
            status_code=HTTP_200_OK)
async def get_one_post(request: Request,
                       blog_id: uuid.UUID,
                       post_id: int,
                       user: Record = Depends(is_auth),
                       post_repository: PostRepository = Depends(PostRepository),
                       view_repository: ViewRepository = Depends(ViewRepository),
                       like_repository: LikeRepository = Depends(LikeRepository),
                       ):
    access = await has_access(request=request, blog_id=blog_id, raise_exception=False)

    post = await post_repository.get_post(access=bool(access), post_id=post_id)

    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=err_resp.ID_NOTFOUND)

    if not await view_repository.is_viewed_post(post_id=post_id, user_id=user.id):
        await view_repository.set_view(post_id=post_id, user_id=user.id)

    is_liked = await like_repository.is_liked_post(post_id=post_id, user_id=user.id)

    return {"is_access": bool(access),
            "is_liked": is_liked,
            "post": post}


@router.post("/{blog_id}/posts/{post_id}/like/",
             status_code=HTTP_200_OK)
async def post_like(blog_id: uuid.UUID,
                    post_id: int,
                    user: Record = Depends(is_auth),
                    post_repository: PostRepository = Depends(PostRepository),
                    like_repository: LikeRepository = Depends(LikeRepository)):
    if not await post_repository.check_post_exists_by_id(post_id=post_id, blog_id=blog_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=err_resp.ID_NOTFOUND)

    await like_repository.toggle_like(post_id=post_id, user_id=user.id)
    return {"status": "ok"}


@router.get("/posts/last/",
            dependencies=[Depends(is_auth)],
            status_code=HTTP_200_OK)
async def post_last(repository: PostRepository = Depends(PostRepository)):
    return await repository.get_last_posts(limit=5)
