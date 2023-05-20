def up():
    return """CREATE TABLE IF NOT EXISTS post_commentaries(id SERIAL PRIMARY KEY, post_id integer references posts(id), author_id integer references users(id), text text);"""


def down():
    return """DROP TABLE IF EXISTS post_commentaries;"""
