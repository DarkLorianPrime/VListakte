def up():
    return """CREATE TABLE IF NOT EXISTS post_commentary_likes(id serial primary key, comment_id int references post_commentaries(id), user_id int references users(id), post_id int references posts(id))"""


def down():
    return """DROP TABLE IF EXISTS post_commentary_likes"""
