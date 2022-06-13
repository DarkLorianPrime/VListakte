def up():
    return """
        CREATE TABLE IF NOT EXISTS Blog(
        id SERIAL PRIMARY KEY, title text, description text default '',
        created_at timestamp, updated_at timestamp, owner_id INTEGER);
        CREATE TABLE IF NOT EXISTS Blog_author(id SERIAL PRIMARY KEY, author_id INTEGER, blog_id INTEGER);
    """


def down():
    return """DROP TABLE Blog; DROP TABLE Blog_author"""
