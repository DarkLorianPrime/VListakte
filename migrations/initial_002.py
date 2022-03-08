import os
from datetime import datetime

from databases import Database

from libraries.database import insert_migration, delete_migration


async def nextmigration(db: Database):
    await insert_migration(db, os.path.basename(__file__).split(".")[0], datetime.now())


async def rollbackmigration(db: Database):
    timestamp = datetime.now()
    name = os.path.basename(__file__)
    await delete_migration(db, name, timestamp)
