def up():
    return """CREATE TABLE IF NOT EXISTS Roles(id SERIAL PRIMARY KEY, Name text);
    CREATE TABLE IF NOT EXISTS Roles_UsersAccount(id SERIAL PRIMARY KEY, role_id INTEGER, user_id INTEGER)"""


def down():
    return """DROP TABLE Roles; DROP TABLE Roles_UsersAccount"""
