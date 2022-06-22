def up():
    return """CREATE TABLE IF NOT EXISTS Roles(id SERIAL PRIMARY KEY, Name text);
    CREATE TABLE IF NOT EXISTS Roles_Users(id SERIAL PRIMARY KEY, role_id INTEGER references Roles(id), user_id INTEGER references users(id))"""


def down():
    return """DROP TABLE Roles; DROP TABLE Roles_Users"""
