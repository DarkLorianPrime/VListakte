import os
from datetime import datetime

from sqlalchemy.engine import Engine

from libraries.database_migrator import insert_migration, delete_migration


def nextmigration(db: Engine):
    db.execute("""CREATE TABLE Account(id SERIAL PRIMARY KEY, name VARCHAR(255), surname VARCHAR(255), password VARCHAR(255), email VARCHAR(255))""")
    insert_migration(db, os.path.basename(__file__).split(".")[0], datetime.now())


def rollbackmigration(db: Engine):
    timestamp = datetime.now()
    name = os.path.basename(__file__)
    db.execute("""DROP TABLE Account""")
    delete_migration(db, name, timestamp)
