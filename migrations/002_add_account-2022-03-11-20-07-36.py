def up():
    return "CREATE TABLE IF NOT EXISTS Account(id SERIAL PRIMARY KEY, name text, surname text, password text, email text)"


def down():
    return "DROP TABLE Account"
