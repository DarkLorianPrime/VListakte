def up():
    return """
        CREATE TABLE IF NOT EXISTS Blogs(id SERIAL PRIMARY KEY, title text, description text default '',
        created_at timestamp, updated_at timestamp, owner_id INTEGER references users(id));
        CREATE TABLE IF NOT EXISTS Blog_authors(id SERIAL PRIMARY KEY, author_id INTEGER references users(Id), blog_id INTEGER references blogs(id));
    """


def down():
    return """DROP TABLE Blog_authors; DROP TABLE Blogs;"""
