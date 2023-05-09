import asyncio
import sys

import importlib
import os
import shutil
import importlib.util
import traceback
from datetime import datetime

import uvicorn

from libraries.database.migrator import Migrations
from libraries.orm.database import db
from libraries.utils.exceptions import MigratorError
from libraries.utils.files import startswith_check_file, endswith_check_file
import nest_asyncio

nest_asyncio.apply()

async def first_migration() -> None:
    """
    :return: None
    Description: Makes the first migration if it has not been done.
    """

    module = importlib.import_module(startswith_check_file("001_initial", "migrations")[0].split(".")[0])
    await db.execute(module.up())


async def prefirstmigrate() -> None:
    """
    :return: None
    Description: Creates the basis for migration
    """

    if "migrations" not in os.listdir():
        os.mkdir("migrations")

    if not startswith_check_file("001_initial", "migrations"):
        shutil.copy("libraries/examples/migration_example_001.py",
                    f"migrations/001_initial-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.py")


async def migrate(_) -> None:
    """
    :param _: Not used in this function
    :return: None
    Description: Allows you to roll out new migrations, if they do not exist yet.
    """
    await prefirstmigrate()

    if not await Migrations.table_exists():
        await first_migration()

    files_list = endswith_check_file(".py", "migrations")
    files_list = list(map(lambda filename: filename.strip(".py"), files_list))
    for file in sorted(files_list):
        if await Migrations.entry_exists(name=file):
            continue

        timestamp = datetime.now()

        module = importlib.import_module(file)
        for small_module in module.up().split(";"):
            if small_module and small_module != ' ':
                await db.execute(small_module)
                await Migrations.objects().insert(timestamp=timestamp, name=file)

        print(f"successful migration created: {file}")


async def rollback_common() -> list:
    """
    :return: list of entries that can be rolled back.
    Description: General method
    """
    if not await Migrations.table_exists():
        raise MigratorError("No migration was applied.")

    query = Migrations.objects().order_by(Migrations.timestamp, "DESC")
    data = await query.all().values()
    return data


async def rollback_all(_) -> None:
    """
    :param _: Not used in this function
    :return: None.
    Description: Rolls back all migrations
    """
    await prefirstmigrate()
    data = await rollback_common()
    for entry in data:
        module = importlib.import_module(entry[1])
        for small_module in module.down().split(";"):
            if small_module and small_module != ' ':
                try:
                    await db.execute(small_module)
                    await Migrations.objects().filter(Migrations.name == entry[1]).delete()
                except:
                    print(f"table {entry[1]} does not exists!")

        print(f"successful migration rollback: {entry[1]}")


async def rollback(args: list) -> None:
    """
    :param args: Allows you to take the necessary arguments
    :return: None.
    Description: Rolls back the last migration, or if --step=N is specified, rolls back the last N migrations.
    """
    print(123)
    data = await rollback_common()
    steps = 1
    if len(args) == 4:
        steps_timely = args[3].split("=")[1]
        if steps_timely.isdigit():
            steps = int(steps_timely)
    steps = len(data) if steps > len(data) else steps

    for step in range(0, steps):
        module = importlib.import_module(data[step][1])
        for small_module in module.down().split(";"):
            if small_module and small_module != ' ':
                await db.execute(small_module)
                await Migrations.objects().filter(Migrations.name == data[step][1]).delete()
        await Migrations.objects().filter(Migrations.name == data[step][1]).delete()
        print(f"successful migration rollback: {data[step][1]}")


async def refresh(args: list) -> None:
    """
    :param args: Not used in this function
    :return: None.
    Description: First deletes all migrations, then rolls them again.
    """

    try:
        await rollback_all(args)
    except MigratorError as e:
        print(e)
    await migrate(args)


async def createmigration(args: list) -> None:
    """
    :param args: Allows you to take the necessary arguments
    :return: None
    """
    if len(args) != 3:
        raise MigratorError("Please specify the migration ID (for examples: 001_cerera)")

    shutil.copy("libraries/examples/migration_example.py",
                f"migrations/{args[2]}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.py")


async def run_server():
    await db.connect()
    main_module = importlib.import_module('main')
    uvicorn.run(main_module.app, port=8000, host="0.0.0.0")
    print("stop server")
    await db.disconnect()


migrator_command = {
    "rollback": rollback,
    "reset": rollback_all,
    "migrate": migrate,
    "refresh": refresh,
    "makemigrations": createmigration
}

command = {
    "runserver": run_server
}


def default(_):
    raise MigratorError(f"For migrator need one in list arguments: {''.join(i for i in migrator_command.keys())}")


async def main() -> None:
    sys.path.append("migrations")
    await db.connect()
    try:
        args = sys.argv
        if len(args) >= 3:
            await migrator_command.get(args[2], default)(args)

        if len(args) == 2:
            await command.get(args[1], default)()

        if len(args) < 2:
            raise MigratorError("Too few arguments.")

    except Exception as e:
        print(traceback.format_exc())
        await db.disconnect()
    finally:
        await db.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
