import importlib
import inspect
import os
import shutil
import sys
from datetime import datetime

from libraries.database.database_migrator import MigratorORM
from libraries.database.new.field_types import ManyToMany
from libraries.database.new.models import Model
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

    def migrate(self):
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

    def make_migrations(self):
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


sys.path.append("migrations1")
MigratorORM().connect()
Migrate().make_migrations()
#Migrate().get_last_migration()
Migrate().migrate()
