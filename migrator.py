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


async def first_migration(db: Database) -> None:
    """
    :param db: The database to work
    :return: None.
    Description: Makes the first migration if it has not been done.
    """

    module = importlib.import_module("initial_001")
    await module.nextmigration(db)


async def prefirstmigrate() -> None:
    """
    :return: None.
    Description: Creates the basis for migration
    """

    if "migrations" not in os.listdir():
        os.mkdir("migrations")
    if "initial_001.py" not in os.listdir(os.getcwd() + "\\migrations"):
        shutil.copy("libraries\\examples\\migration_example.py", "migrations/initial_001.py")


async def migrate(db: Database, args) -> None:
    """
    :param db: The database to work
    :param args: Not used in this function
    :return: None.
    Description: Allows you to roll out new migrations, if they do not exist yet.
    """

    await prefirstmigrate()
    sys.path.append("migrations")

    if not await table_exists(db, "migrations"):
        await first_migration(db)
    files_list = list(filter(lambda file: file.endswith(".py"), os.listdir("migrations")))
    files_list = list(map(lambda filename: filename.strip(".py"), files_list))
    for file in files_list:
        if await entry_exists(db, "migrations", {"name": file}):
            continue

        module = importlib.import_module(file)
        await module.nextmigration(db)


async def rollback_common(db: Database) -> list:
    """
    :param db: The database to work
    :return: list of entries that can be rolled back.
    Description: General method
    """

    sys.path.append("migrations")

    if not await table_exists(db, "migrations"):
        raise CreatorError("No migration was applied.")

    data = await get_filtered_entries(db, "migrations", None, "timestamp desc")
    return data


async def rollback_all(db: Database, args) -> None:
    """
    :param db: The database to work
    :param args: Not used in this function
    :return: None.
    Description: Rolls back all migrations
    """

    data = await rollback_common(db)

    for entry in data:
        module = importlib.import_module(entry[1])
        await module.rollbackmigration(db)


async def rollback(db: Database, args) -> None:
    """
    :param db: The database to work
    :param args: Allows you to take the necessary arguments
    :return: None.
    Description: Rolls back the last migration, or if --step=N is specified, rolls back the last N migrations.
    """

    data = await rollback_common(db)
    steps = 1

    if len(args) == 3:
        steps_timely = args[2].split("=")[1]
        if steps_timely.isdigit():
            steps = int(steps_timely)

    steps = len(data) if steps > len(data) else steps

    for step in range(0, steps):
        module = importlib.import_module(data[step][1])
        await module.rollbackmigration(db)


async def refresh(db: Database, args) -> None:
    """
    :param db: The database to work
    :param args: Not used in this function
    :return: None.
    Description: First deletes all migrations, then rolls them again.
    """

    try:
        await rollback_all(db, args)
    except CreatorError as e:
        print(e)
    await migrate(db, args)


command = {
    "rollback": rollback,
    "reset": rollback_all,
    "migrate": migrate,
    "refresh": refresh
}


async def main() -> None:
    db = await get_database_instance()
    args = sys.argv

    if len(args) < 2:
        raise CreatorError("Too few arguments.")

    await command[args[1]](db, args)
    await db.disconnect()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
