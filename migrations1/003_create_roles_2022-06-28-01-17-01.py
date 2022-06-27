def up():
    return """CREATE TABLE IF NOT EXISTS roles (id serial PRIMARY KEY, name varchar);
    CREATE TABLE IF NOT EXISTS users_Roles(users_id INTEGER references users(id), Roles_id INTEGER references Roles(id))"""


def down():
    return "DROP TABLE IF EXISTS roles; DROP TABLE IF EXISTS users_Roles;" 