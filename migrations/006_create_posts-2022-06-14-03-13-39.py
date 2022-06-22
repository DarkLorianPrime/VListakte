def up():
    return """CREATE TABLE IF NOT EXISTS posts(id SERIAL PRIMARY KEY, title varchar(100), text text, is_published boolean, created_at timestamp, author_id integer references users(id), blog_id integer references blog(id))"""


def down():
    return """DROP TABLE IF EXISTS posts"""
