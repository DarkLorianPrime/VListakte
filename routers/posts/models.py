from libraries.orm.core import Model
from libraries.orm.fields import SerialField, StringField, TextField, BooleanField, TimestampField, IntegerField, \
    UUIDField


class Post(Model):
    tablename = "posts"
    id = SerialField()
    title = StringField(max_length=100)
    text = TextField()
    is_published = BooleanField()
    created_at = TimestampField()
    author_id = IntegerField()
    blog_id = UUIDField()