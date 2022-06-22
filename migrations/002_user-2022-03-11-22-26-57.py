def up():
    return """CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, password VARCHAR(128), last_login timestamptz default NULL, is_admin bool default false, username VARCHAR(150), registration_data timestamptz DEFAULT now())"""


def down():
    return """DROP TABLE UserAccount"""
