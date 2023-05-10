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


class PostLike(Model):
    tablename = "post_likes"
    id = SerialField()
    post_id = IntegerField()
    user_id = IntegerField()


class PostView(Model):
    tablename = "post_views"
    id = SerialField()
    post_id = IntegerField()
    user_id = IntegerField()


class PostCommentaries(Model):
    tablename = "post_commentaries"
    id = SerialField()
    post_id = IntegerField()
    author_id = IntegerField()
    text = TextField()


class PostCommentaryLike(Model):
    tablename = "post_commentary_likes"
    id = SerialField()
    post_id = IntegerField()
    user_id = IntegerField()
    comment_id = IntegerField()