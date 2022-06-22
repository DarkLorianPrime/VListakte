def up():
    return """
        CREATE TABLE IF NOT EXISTS Blog(
        id SERIAL PRIMARY KEY, title text, description text default '',
        created_at timestamp, updated_at timestamp, owner_id INTEGER references users(id));
        CREATE TABLE IF NOT EXISTS Blog_author(id SERIAL PRIMARY KEY, author_id INTEGER references users(Id), blog_id INTEGER);
    """


def down():
    return """DROP TABLE Blog; DROP TABLE Blog_author"""
