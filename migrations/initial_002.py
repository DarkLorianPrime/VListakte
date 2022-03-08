import os
from datetime import datetime

from databases import Database

from libraries.database import insert_migration, delete_migration


async def nextmigration(db: Database):
    await db.execute(
        """CREATE TABLE Account(id SERIAL PRIMARY KEY, name VARCHAR(255), surname VARCHAR(255), password VARCHAR(255), email VARCHAR(255))""")
    await insert_migration(db, os.path.basename(__file__).split(".")[0], datetime.now())


async def rollbackmigration(db: Database):
    timestamp = datetime.now()
    name = os.path.basename(__file__)
    await db.execute("""DROP TABLE Account""")
    await delete_migration(db, name, timestamp)
