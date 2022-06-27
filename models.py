from libraries.database.new.field_types import String, Timestamp, Boolean, UUID, ManyToMany, Text, ForeignKey
from libraries.database.new.models import Model


class Users(Model):
    password = String(max_length=128)
    last_login = Timestamp(default="NULL")
    username = String(max_length=150)
    registration_date = Timestamp(default="now()")
    token = UUID()

    class Meta:
        table_name = "users"


class Roles(Model):
    name = String()
    roles_users = ManyToMany(Users)

    class Meta:
        table_name = "roles"


class Blogs(Model):
    title = String()
    description = Text(default="")
    created_at = Timestamp(default="now()")
    updated_at = Timestamp(default="now()")
    owner_id = ForeignKey(Users)
    blogs_authors = ManyToMany(Users)

    class Meta:
        table_name = "blogs"


class Posts(Model):
    title = String(max_length=100)
    text = Text()
    is_published = Boolean()
    created_at = Timestamp(default="now()")
    author_id = ForeignKey(Users)
    blog_id = ForeignKey(Blogs)
    posts_like = ManyToMany(Users)
    posts_views = ManyToMany(Users)

    class Meta:
        table_name = "posts"


class Commentaries(Model):
    post_id = ForeignKey(Posts)
    author_id = ForeignKey(Users)
    text = Text()
    commentaries_like = ManyToMany(Posts)

    class Meta:
        table_name = "commentaries"
