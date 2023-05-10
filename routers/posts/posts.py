import uuid
from datetime import datetime
from typing import Optional

from databases.backends.postgres import Record
from fastapi import APIRouter, Depends, Form, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_204_NO_CONTENT

from extras.validators import is_auth, has_access
from libraries.orm.fields import _in
from routers.posts.models import Post, PostLike, PostView, PostCommentaries

router = APIRouter()


@router.get("/{blog_id}/posts/")
async def get_all_posts(request: Request, blog_id: uuid.UUID, user: Record = Depends(is_auth), published: bool = True):
    access = await has_access(request=request, process_id=blog_id, raise_exception=False)
    return_dict = {"has_access": bool(access), "posts": []}

    published = published if access else True
    posts = await Post.filter(Post.blog_id == blog_id, Post.is_published == published).all().values()
    posts_ids = [str(post.id) for post in posts]

    likes = await PostLike.filter(_in(PostLike.post_id, posts_ids), PostLike.user_id == user.id).all().values("post_id")
    likes_ids = [like.post_id for like in likes]

    views = await PostView.filter(_in(PostView.post_id, posts_ids), PostView.user_id == user.id).all().values("post_id")
    views_ids = [view.post_id for view in views]

    for post in posts:
        post = dict(post)
        post["is_liked"] = post["id"] in likes_ids
        post["is_viewed"] = post["id"] in views_ids
        return_dict["posts"].append(post)

    return return_dict


@router.post("/{process_id}/posts/")
async def create_post(process_id: uuid.UUID,
                      user: Record = Depends(has_access),
                      title: str = Form(...),
                      text: str = Form(...),
                      is_published: bool = Form(...)):
    post = await Post.objects().filter(Post.blog_id == process_id, Post.title == title).exists()

    if post:
        raise HTTPException(status_code=HTTP_422_UNPROCESSABLE_ENTITY, detail="Post with this title already exists")

    values = {"title": title, "text": text, "is_published": is_published, "created_at": datetime.now(),
              "author_id": user.id, "blog_id": process_id}
    await Post.objects().insert(**values)

    return {key: str(value) for key, value in values.items()}


@router.delete("/{process_id}/posts/{post_id}/", dependencies=[Depends(has_access)], status_code=HTTP_204_NO_CONTENT)
async def delete_post(process_id: int, post_id: int):
    await Post.filter(Post.id == post_id, Post.blog_id == process_id).delete()
    await PostView.filter(PostView.post_id == post_id).delete()
    await PostLike.filter(PostLike.post_id == post_id).delete()
    await PostCommentaries.filter(PostCommentaries.post_id == post_id).delete()


@router.patch("/{process_id}/posts/{post_id}/", dependencies=[Depends(has_access)], status_code=200)
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
        await Post.objects().filter(Post.id == post_id, Post.blog_id == process_id).update(params)

    return {"status": "ok", **params}


@router.get("/{process_id}/posts/{post_id}/", status_code=HTTP_200_OK)
async def get_one_post(request: Request, process_id: uuid.UUID, post_id: int, user: Record = Depends(is_auth)):
    if not await PostView.filter(PostView.post_id == post_id, PostView.user_id == user.id).exists():
        await PostView.objects().insert(post_id=post_id, user_id=user.id)

    is_liked = await PostLike.filter(PostLike.post_id == post_id, PostLike.user_id == user.id).exists()
    access = await has_access(request=request, process_id=process_id, raise_exception=False)
    returned_values = {"is_access": bool(access)}

    query = Post.filter(Post.id == post_id)
    if not access:
        query = query.filter(Post.is_published == True)

    post = await query.first()
    if post is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Post with this ID not found")

    returned_values["is_liked"] = is_liked
    returned_values["post"] = post

    return returned_values


@router.post("/{process_id}/posts/{post_id}/like/", status_code=HTTP_200_OK)
async def post_like(process_id: uuid.UUID,
                    post_id: int,
                    user: Record = Depends(is_auth)):
    post = await Post.filter(Post.id == post_id, Post.blog_id == process_id).exists()

    if not post:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail={"error": "Post not found"})

    like = await PostLike.filter(PostLike.post_id == post_id, PostLike.user_id == user.id).exists()

    if not like:
        await PostLike.objects().insert(post_id=post_id, user_id=user.id)
        return {"status": "ok"}

    await PostLike.filter(PostLike.post_id == post_id, PostLike.user_id == user.id).delete()
    return {"status": "ok"}


@router.get("/posts/last/", dependencies=[Depends(is_auth)], status_code=HTTP_200_OK)
async def post_last():
    posts = Post.objects().order_by(Post.created_at, "DESC").all()[:5]

    return posts
