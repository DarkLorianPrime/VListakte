from libraries.orm.core import Model
from libraries.orm.fields import UUIDField, TextField, TimestampField, IntegerField, SerialField


class Blog(Model):
    tablename = "blogs"
    id = UUIDField(primary_key=True)
    title = TextField()
    description = TextField(default='')
    created_at = TimestampField()
    updated_at = TimestampField()
    owner_id = IntegerField()


class BlogAuthors(Model):
    tablename = "blog_authors"
    id = SerialField()
    author_id = IntegerField()
    blog_id = UUIDField()
