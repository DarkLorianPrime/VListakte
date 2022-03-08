import sys

import asyncio
import importlib
import os
import shutil
import importlib.util
from warnings import warn

from databases import Database

from libraries.database import get_database_instance, get_filtered_entries, table_exists, entry_exists
from libraries.exceptions import CreatorError


def _import_module(name):
    warn("This module is deprecated and will be removed in a next release.", DeprecationWarning, stacklevel=2)
    spec = importlib.util.spec_from_file_location(name, f"migrations\\{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


async def first_migration(db: Database):
    module = importlib.import_module("initial_001")
    await module.nextmigration(db)


async def prefirstmigrate():
    if "migrations" not in os.listdir():
        os.mkdir("migrations")
    if "initial_001.py" not in os.listdir(os.getcwd() + "\\migrations"):
        shutil.copy("libraries\\examples\\migration_example.py", "migrations/initial_001.py")


async def migrate(db: Database):
    await prefirstmigrate()
    sys.path.append("migrations")
    if not await table_exists(db, "migrations"):
        await first_migration(db)
    for file in [files.split(".")[0] for files in os.listdir("migrations")[0:-1]]:
        if await entry_exists(db, "migrations", {"name": file}):
            continue
        module = importlib.import_module(file)
        await module.nextmigration(db)


async def rollback_common(db: Database):
    sys.path.append("migrations")
    if not await table_exists(db, "migrations"):
        raise CreatorError("No migration was applied.")
    data = await get_filtered_entries(db, "migrations", None, "timestamp desc")
    return data


async def rollback_all(db: Database):
    data = await rollback_common(db)
    for entry in data:
        module = importlib.import_module(entry[1])
        await module.rollbackmigration(db)


async def rollback(db: Database):
    data = await rollback_common(db)
    module = importlib.import_module(data[0][1])
    await module.rollbackmigration(db)


command = {
    "rollback": rollback,
    "rollbackall": rollback_all,
    "migrate": migrate
}


async def main():
    db = await get_database_instance()
    args = sys.argv
    if len(args) != 2:
        raise CreatorError("Too many or too few arguments.")
    await command[args[1]](db)
    await db.disconnect()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
