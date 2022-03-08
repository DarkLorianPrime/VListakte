import os
from datetime import datetime

from databases import Database

from libraries.database import insert_migration, delete_migration


async def nextmigration(db: Database):
    timestamp = datetime.now()
    name = os.path.basename(__file__).split(".")[0]
    await db.execute("""ALTER TABLE Account ADD Phone CHARACTER VARYING(20) NOT NULL DEFAULT '7 (000) 000 00-00'""")
    await db.execute("""ALTER TABLE Account ADD Phone_mom CHARACTER VARYING(20) NOT NULL DEFAULT '7 (000) 000 00-00'""")
    await insert_migration(db, name, timestamp)


async def rollbackmigration(db: Database):
    timestamp = datetime.now()
    name = os.path.basename(__file__)
    await db.execute("""ALTER TABLE Account DROP Phone""")
    await db.execute("""ALTER TABLE Account DROP Phone_mom""")
    await delete_migration(db, name, timestamp)
