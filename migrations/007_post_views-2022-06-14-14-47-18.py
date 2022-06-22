def up():
    return """CREATE TABLE IF NOT EXISTS views(id SERIAL PRIMARY KEY, post_id integer references posts(id))"""


def down():
    return """DROP TABLE IF EXISTS views"""
