import os
from datetime import datetime

import dotenv
import sqlalchemy

from libraries.utils.extra_features import Singleton

dotenv.load_dotenv("libraries/.env")


class MigratorORM(Singleton):
    __host = os.getenv("host")
    __database = os.getenv("db")
    __user = os.getenv("user")
    __password = os.getenv("password")
    connect = "postgresql+psycopg2"
    url = sqlalchemy.engine.URL.create(connect, username=__user, password=__password, host=__host, database=__database)
    db = sqlalchemy.create_engine(url)

    def connect(self):
        self.db.connect()

    def disconnect(self):
        self.db.dispose()

    def entry_exists(self, table_name: str, values: dict):
        query_where = ", ".join(f"{k}='{v}'" for k, v in values.items())
        query = "SELECT exists(select 1 FROM %s where %s)" % (table_name, query_where)
        data = self.db.execute(query)
        return data.one()[0]

    def table_exists(self, table_name: str):
        query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '%s');" % table_name
        data = self.db.execute(query)
        return data.one()[0]

    def insert_migration(self, name: str):
        timestamp = datetime.now()
        query = """INSERT INTO migrations(name, timestamp) VALUES('%s', '%s')""" % (name, timestamp)
        self.db.execute(query)
        print(f"successfully inserted migration: {name}")

    def delete_migration(self, name: str):
        print(f"successful migration rollback: {name}")
        if name.startswith("001_initial"):
            return
        name = name.split('.')[0]
        query = """DELETE FROM migrations WHERE name='%s'""" % name
        self.db.execute(query)

    def get_filtered_entries(self, table_name: str, values: dict = None, orderby: str = None):
        query = "SELECT * FROM %s " % table_name
        if values is not None:
            query += "where %s" % ", ".join(f"{k}='{v}'" for k, v in values.items())
        if orderby is not None:
            query += f"order by {orderby}"
        data = self.db.execute(query)
        return data.fetchall()
