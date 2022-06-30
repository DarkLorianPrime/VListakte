import importlib
import inspect
import os
import shutil
import sys
from datetime import datetime

from libraries.database.database_migrator import MigratorORM
from libraries.database.new.field_types import ManyToMany
from libraries.database.new.models import Model
from libraries.utils.exceptions import MigratorError
from libraries.utils.files import startswith_check_file, endswith_check_file


class Migrate:
    def __init__(self):
        self.query = ""
        self.folder = "migrations1"

    def linenumber_of_member(self, m):
        """
        TIMELY COSTYL
        :param m:
        :return:
        """
        try:
            return inspect.getsourcelines(m[1])[1]
        except AttributeError:
            return -1

    def first_migration(self) -> None:
        """
        :return: None
        Description: Makes the first migration if it has not been done.
        """
        module = importlib.import_module(startswith_check_file("001_initial", self.folder)[0].split(".")[0])
        MigratorORM().db.execute(module.up())

    def prefirstmigrate(self) -> None:
        """
        :return: None
        Description: Creates the basis for migration
        """
        migrator = MigratorORM()
        migrator.connect()
        if self.folder not in os.listdir():
            os.mkdir(self.folder)

        if not startswith_check_file("001_initial", self.folder):
            shutil.copy("libraries/examples/migration_example_001.py",
                        f"{self.folder}/001_initial-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.py")

        if not migrator.table_exists(self.folder):
            self.first_migration()

    def get_last_migration(self):
        return os.listdir(self.folder)[-2].split("_")[0]

    def migrate(self, _):
        migrator = MigratorORM()

        self.prefirstmigrate()

        files_list = endswith_check_file(".py", self.folder)
        files_list = list(map(lambda filename: filename.strip(".py"), files_list))

        for file in files_list:
            if migrator.entry_exists("migrations", {"name": file}):
                continue

            module = importlib.import_module(file)
            migrator.db.execute(module.up())
            migrator.insert_migration(file)

        migrator.disconnect()

    def make_migrations(self, _):
        migrator = MigratorORM()
        self.prefirstmigrate()

        module = importlib.import_module(startswith_check_file("models")[0].split(".")[0])
        classes = inspect.getmembers(sys.modules[module.__name__], inspect.isclass)
        classes.sort(key=self.linenumber_of_member)
        filtered_classes = list(filter(lambda x: x[1] in Model.__subclasses__(), classes))
        last_element = int(self.get_last_migration())

        for filtered_class in filtered_classes:
            mtm = False
            migration_id = "".join(list("000")[:-len(str(last_element))]) + str(last_element := last_element + 1)
            query = ""
            query_args = []

            table_name = getattr(filtered_class[1].Meta(), "table_name", filtered_class[1].__name__)

            if not migrator.table_exists(table_name):
                query = f"CREATE TABLE IF NOT EXISTS {table_name} (id serial PRIMARY KEY, "

            for key, attribute in filtered_class[1].__dict__.items():

                if isinstance(attribute, ManyToMany):
                    mtm = attribute
                    continue

                if key in ["__module__", "__doc__", "Meta"]:
                    continue

                query_args.append(f"{key} {attribute}")

            query += ", ".join(query_args) + ');'
            date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

            file_name = f"{migration_id}_create_{table_name}_{date}.py"

            if list(filter(lambda x: f"create_{table_name}" in x, os.listdir(self.folder))):
                continue

            if mtm:
                query += f"\n    {mtm}"
                table_name += f"; DROP TABLE IF EXISTS {mtm.name}"

            with open(f"{self.folder}/{file_name}", "w", encoding="UTF-8") as file:
                file.write(f"""def up():\n    return "\"\"{query}"\"\"\n\n\ndef down():\n    return "DROP TABLE IF EXISTS {table_name};" """)

            print(f"create {file_name}")

    def rollback_common(self) -> list:
        """
        :return: list of entries that can be rolled back.
        Description: General method
        """
        db = MigratorORM()
        if not db.table_exists(self.folder):
            raise MigratorError("No migration was applied.")

        data = db.get_filtered_entries("migrations", None, "timestamp desc")
        return data

    def rollback_all(self, _) -> None:
        """
        :param _: Not used in this function
        :return: None.
        Description: Rolls back all migrations
        """
        db = MigratorORM()
        db.connect()
        self.prefirstmigrate()
        data = self.rollback_common()
        for entry in data:
            module = importlib.import_module(entry[1])
            db.db.execute(module.down())
            db.delete_migration(entry[1])

    def rollback(self, args: list) -> None:
        """
        :param args: Allows you to take the necessary arguments
        :return: None.
        Description: Rolls back the last migration, or if --step=N is specified, rolls back the last N migrations.
        """

        data = self.rollback_common()
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

    def refresh(self, _) -> None:
        """
        :return: None.
        Description: First deletes all migrations, then rolls them again.
        """

        try:
            self.rollback_all(_)
        except MigratorError as e:
            print(e)
        self.migrate(_)


sys.path.append("migrations1")

mgr = Migrate()
command = {
    "rollback": mgr.rollback,
    "reset": mgr.rollback_all,
    "migrate": mgr.migrate,
    "refresh": mgr.refresh,
    "makemigrations": mgr.make_migrations
}


def main() -> None:
    sys.path.append("migrations")
    args = sys.argv
    if len(args) < 2:
        raise MigratorError("Too few arguments.")
    MigratorORM().connect()
    command[args[1]](args)
    MigratorORM().disconnect()


if __name__ == "__main__":
    main()
