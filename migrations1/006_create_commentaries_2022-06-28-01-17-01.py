def up():
    return """CREATE TABLE IF NOT EXISTS commentaries (id serial PRIMARY KEY, post_id INTEGER references posts(id), author_id INTEGER references users(id), text text);
    CREATE TABLE IF NOT EXISTS posts_Commentaries(posts_id INTEGER references posts(id), Commentaries_id INTEGER references Commentaries(id))"""


def down():
    return "DROP TABLE IF EXISTS commentaries; DROP TABLE IF EXISTS posts_Commentaries;" 