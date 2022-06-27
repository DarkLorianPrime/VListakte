def up():
    return """CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, password varchar(128), last_login timestamp  DEFAULT NULL, username varchar(150), registration_date timestamp  DEFAULT now(), token uuid);"""


def down():
    return "DROP TABLE IF EXISTS users;" 