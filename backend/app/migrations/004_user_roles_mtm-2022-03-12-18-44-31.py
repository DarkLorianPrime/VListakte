def up():
    return """CREATE TABLE IF NOT EXISTS Roles(id SERIAL PRIMARY KEY, Name text);
    CREATE TABLE IF NOT EXISTS Roles_Users(id SERIAL PRIMARY KEY, role_id INTEGER references Roles(id), user_id INTEGER references users(id));
    INSERT INTO Roles (Name) values ('User'), ('Administrator');"""


def down():
    return """DROP TABLE IF EXISTS Roles_Users; DROP TABLE IF EXISTS Roles;"""
