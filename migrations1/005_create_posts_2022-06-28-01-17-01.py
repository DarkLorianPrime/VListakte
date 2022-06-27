def up():
    return """CREATE TABLE IF NOT EXISTS posts (id serial PRIMARY KEY, title varchar(100), text text, is_published bool , created_at timestamp  DEFAULT now(), author_id INTEGER references users(id), blog_id INTEGER references blogs(id));
    CREATE TABLE IF NOT EXISTS users_Posts(users_id INTEGER references users(id), Posts_id INTEGER references Posts(id))"""


def down():
    return "DROP TABLE IF EXISTS posts; DROP TABLE IF EXISTS users_Posts;" 