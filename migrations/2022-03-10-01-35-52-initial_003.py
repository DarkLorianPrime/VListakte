import os
from datetime import datetime

from sqlalchemy.engine import Engine

from libraries.database_migrator import insert_migration, delete_migration


def nextmigration(db: Engine):
    timestamp = datetime.now()
    name = os.path.basename(__file__).split(".")[0]
    db.execute("""ALTER TABLE Account ADD Phone CHARACTER VARYING(20) NOT NULL DEFAULT '7 (000) 000 00-00'""")
    db.execute("""ALTER TABLE Account ADD Phone_mom CHARACTER VARYING(20) NOT NULL DEFAULT '7 (000) 000 00-00'""")
    insert_migration(db, name, timestamp)


def rollbackmigration(db: Engine):
    timestamp = datetime.now()
    name = os.path.basename(__file__)
    db.execute("""ALTER TABLE Account DROP Phone""")
    db.execute("""ALTER TABLE Account DROP Phone_mom""")
    delete_migration(db, name, timestamp)
