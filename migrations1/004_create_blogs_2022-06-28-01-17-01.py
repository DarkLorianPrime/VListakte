def up():
    return """CREATE TABLE IF NOT EXISTS blogs (id serial PRIMARY KEY, title varchar, description text, created_at timestamp  DEFAULT now(), updated_at timestamp  DEFAULT now(), owner_id INTEGER references users(id));
    CREATE TABLE IF NOT EXISTS users_Blogs(users_id INTEGER references users(id), Blogs_id INTEGER references Blogs(id))"""


def down():
    return "DROP TABLE IF EXISTS blogs; DROP TABLE IF EXISTS users_Blogs;" 