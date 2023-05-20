def up():
    return """CREATE TABLE IF NOT EXISTS post_likes(id SERIAL PRIMARY KEY, post_id integer references posts(id), user_id integer references users(id))"""


def down():
    return """DROP TABLE IF EXISTS post_likes"""
