import os
from datetime import datetime

from sqlalchemy.engine import Engine

from libraries.database_migrator import insert_migration, delete_migration


def nextmigration(db: Engine):
    timestamp = datetime.now()
    name = os.path.basename(__file__).split(".")[0]
    db.execute("""CREATE TABLE migrations(id SERIAL PRIMARY KEY, name VARCHAR(255), timestamp timestamp(255))""")
    insert_migration(db, name, timestamp)


def rollbackmigration(db: Engine):
    timestamp = datetime.now()
    name = os.path.basename(__file__)
    delete_migration(db, name, timestamp)
    db.execute("""DROP TABLE migrations""")

