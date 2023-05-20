from typing import List
from uuid import UUID

from databases.backends.postgres import Record

from routers.authserver.models import User
from routers.blogs.models import Blog, BlogAuthors
from routers.posts.models import Post


class UserRepository:
    async def is_user_exists(self, user_id: int) -> bool:
        return await User.filter(User.id == user_id).exists()


class BlogRepository:
    async def not_user_owner(self, user_id: int, blog_id: UUID) -> bool:
        if not await UserRepository().is_user_exists(user_id):
            return False

        return not await Blog.filter(Blog.owner_id == user_id, Blog.id == blog_id).exists()

    async def check_blog_exists_title(self, user: Record, title: str) -> bool:
        return await Blog.objects().filter(Blog.owner_id == user.id, Blog.title == title).exists()

    async def check_blog_exists_by_id(self, blog_id: UUID) -> bool:
        return await Blog.filter(Blog.id == blog_id).exists()

    async def create_blog(self, values: dict) -> None:
        values: dict = values.copy()
        values.pop("authors", None)
        await Blog.objects().insert(**values)

    async def delete_authors(self, blog_id: UUID):
        await BlogAuthors.objects().filter(BlogAuthors.blog_id == blog_id).delete()

    async def insert_authors(self, blog_id: UUID, users: set) -> List[Record] | List:
        values = [{"blog_id": blog_id, "author_id": user} for user in users if await self.not_user_owner(user, blog_id)]

        return await BlogAuthors.objects().insert_many(values, "author_id") if values else []

    async def get_all_blogs(self, offset: int, limit: int) -> List[Record]:
        return Blog.objects().all()[int(offset):int(limit)]

    async def get_one_blog_by_id(self, blog_id: UUID) -> Record:
        return await Blog.filter(Blog.id == blog_id).first()

    async def update_blog(self, blog_id: UUID, parameters: dict) -> None:
        parameters: dict = parameters.copy()
        parameters.pop("authors", None)
        await Blog.filter(Blog.id == blog_id).update(parameters)

    async def delete_blog(self, blog_id: UUID) -> None:
        await BlogAuthors.filter(BlogAuthors.blog_id == blog_id).delete()
        await Blog.filter(Blog.id == blog_id).delete()
        await Post.filter(Post.blog_id == blog_id).delete()

class BlogAuthorsRepository:
    async def get_blog_authors_ids(self, blog_id: UUID) -> List[int]:
        authors_ids = await BlogAuthors.filter(BlogAuthors.blog_id == blog_id).all().values("author_id")
        return [author.author_id for author in authors_ids]
