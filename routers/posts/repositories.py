from typing import List, Tuple, Type
from uuid import UUID

from databases.backends.postgres import Record

from libraries.orm.core import Query
from libraries.orm.fields import _in
from routers.posts.models import Post, PostView, PostLike, PostCommentaries


class PostRepository:
    async def check_post_exists_title(self, blog_id: UUID, title: str) -> bool:
        return await Post.objects().filter(Post.blog_id == blog_id, Post.title == title).exists()

    async def check_post_exists_by_id(self, blog_id: UUID, post_id: int) -> bool:
        return await Post.objects().filter(Post.blog_id == blog_id, Post.id == post_id).exists()

    async def create_post(self, parameters: dict) -> None:
        await Post.objects().insert(**parameters)

    async def get_post(self, access: bool, post_id: int) -> Record:
        query = Post.filter(Post.id == post_id)
        if not access:
            query = query.filter(Post.is_published == True)

        return await query.first()

    async def get_posts(self, offset: int, limit: int, blog_id: UUID, published: bool) -> List[Record]:
        posts = await Post.filter(Post.blog_id == blog_id, Post.is_published == published).all()[int(offset):int(limit)]
        return posts

    async def get_last_posts(self, limit: int):
        return Post.objects().filter(Post.is_published == True).order_by(Post.created_at, "DESC").all()[:limit]

    async def get_posts_include_ids(self,
                                    offset: int,
                                    limit: int,
                                    blog_id: UUID,
                                    published: bool) -> tuple[list[str], list[Record]]:
        posts = await self.get_posts(offset, limit, blog_id, published)
        return [str(post.id) for post in posts], posts

    async def get_grouped_param_count(self, model: Type[PostLike] | Type[PostView]) -> List[Record]:
        return await model.objects().group_by("post_id").values("post_id", "count(id)")

    async def get_count_from_grouped(self, post_id: int, result: List[Record]):
        item = {"count": x["count"] for x in result if x.post_id == post_id}
        return item.get("count", 0)

    async def update_post(self, blog_id: UUID, post_id: int, parameters: dict):
        await Post.objects().filter(Post.id == post_id, Post.blog_id == blog_id).update(parameters)

    async def get_model_items(self,
                              model: Type[PostLike] | Type[PostView],
                              posts_ids: List[str],
                              user_id: int) -> List[int]:
        values = await model.filter(_in(model.post_id, posts_ids), model.user_id == user_id).all().values("post_id")
        return [value.post_id for value in values]

    async def delete_post(self, post_id: int, blog_id: UUID) -> None:
        await Post.filter(Post.id == post_id, Post.blog_id == blog_id).delete()
        await PostView.filter(PostView.post_id == post_id).delete()
        await PostLike.filter(PostLike.post_id == post_id).delete()
        await PostCommentaries.filter(PostCommentaries.post_id == post_id).delete()


class ViewRepository:
    async def is_viewed_post(self, post_id: int, user_id: int) -> bool:
        return await PostView.filter(PostView.post_id == post_id, PostView.user_id == user_id).exists()

    async def set_view(self, post_id: int, user_id: int) -> None:
        await PostView.objects().insert(post_id=post_id, user_id=user_id)


class LikeRepository:
    async def is_liked_post(self, post_id: int, user_id: int) -> bool:
        return await PostLike.filter(PostLike.post_id == post_id, PostLike.user_id == user_id).exists()

    async def toggle_like(self, post_id: int, user_id: int) -> None:
        if await self.is_liked_post(post_id=post_id, user_id=user_id):
            return await PostLike.filter(PostLike.post_id == post_id, PostLike.user_id == user_id).delete()

        await PostLike.objects().insert(post_id=post_id, user_id=user_id)
