import sys

import importlib
import os
import shutil
import importlib.util
from datetime import datetime

from libraries.database.database_migrator import MigratorORM
from libraries.utils.exceptions import MigratorError
from libraries.utils.files import startswith_check_file, endswith_check_file


def first_migration() -> None:
    """
    :return: None
    Description: Makes the first migration if it has not been done.
    """

    module = importlib.import_module(startswith_check_file("001_initial", "migrations")[0].split(".")[0])
    MigratorORM().db.execute(module.up())


def prefirstmigrate() -> None:
    """
    :return: None
    Description: Creates the basis for migration
    """

    if "migrations" not in os.listdir():
        os.mkdir("migrations")

    if not startswith_check_file("001_initial", "migrations"):
        shutil.copy("libraries/examples/migration_example_001.py",
                    f"migrations/001_initial-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.py")


def migrate(_) -> None:
    """
    :param _: Not used in this function
    :return: None
    Description: Allows you to roll out new migrations, if they do not exist yet.
    """
    db = MigratorORM()
    db.connect()
    prefirstmigrate()

    if not db.table_exists("migrations"):
        first_migration()

    files_list = endswith_check_file(".py", "migrations")
    files_list = list(map(lambda filename: filename.strip(".py"), files_list))

    for file in files_list:
        if db.entry_exists("migrations", {"name": file}):
            continue

        module = importlib.import_module(file)
        db.db.execute(module.up())
        db.insert_migration(file)


def rollback_common() -> list:
    """
    :return: list of entries that can be rolled back.
    Description: General method
    """
    db = MigratorORM()
    db.connect()
    if not db.table_exists("migrations"):
        raise MigratorError("No migration was applied.")

    data = db.get_filtered_entries("migrations", None, "timestamp desc")
    return data


def rollback_all(_) -> None:
    """
    :param _: Not used in this function
    :return: None.
    Description: Rolls back all migrations
    """
    db = MigratorORM()
    db.connect()
    prefirstmigrate()
    data = rollback_common()
    for entry in data:
        module = importlib.import_module(entry[1])
        db.db.execute(module.down())
        db.delete_migration(entry[1])


def rollback(args: list) -> None:
    """
    :param args: Allows you to take the necessary arguments
    :return: None.
    Description: Rolls back the last migration, or if --step=N is specified, rolls back the last N migrations.
    """

    data = rollback_common()
    steps = 1
    db = MigratorORM()
    db.connect()
    if len(args) == 3:
        steps_timely = args[2].split("=")[1]
        if steps_timely.isdigit():
            steps = int(steps_timely)

    steps = len(data) if steps > len(data) else steps

    for step in range(0, steps):
        module = importlib.import_module(data[step][1])
        db.db.execute(module.down())
        db.delete_migration(data[step][1])


def refresh(args: list) -> None:
    """
    :param args: Not used in this function
    :return: None.
    Description: First deletes all migrations, then rolls them again.
    """

    try:
        rollback_all(args)
    except MigratorError as e:
        print(e)
    migrate(args)


def createmigration(args: list) -> None:
    """
    :param args: Allows you to take the necessary arguments
    :return: None
    """
    if len(args) != 3:
        raise MigratorError("Please specify the migration ID (for examples: 001_cerera)")
    shutil.copy("libraries/examples/migration_example.py",
                f"migrations/{args[2]}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.py")


command = {
    "rollback": rollback,
    "reset": rollback_all,
    "migrate": migrate,
    "refresh": refresh,
    "makemigrations": createmigration
}


def main() -> None:
    sys.path.append("migrations")
    args = sys.argv
    if len(args) < 2:
        raise MigratorError("Too few arguments.")
    command[args[1]](args)
    MigratorORM().disconnect()


if __name__ == "__main__":
    main()
