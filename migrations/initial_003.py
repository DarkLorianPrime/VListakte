import os
from datetime import datetime

from databases import Database

from libraries.database import insert_migration, delete_migration


async def nextmigration(db: Database):
    timestamp = datetime.now()
    name = os.path.basename(__file__).split(".")[0]
    await insert_migration(db, name, timestamp)


async def rollbackmigration(db: Database):
    timestamp = datetime.now()
    name = os.path.basename(__file__)
    await delete_migration(db, name, timestamp)
