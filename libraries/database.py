import hashlib

from databases import Database

from settings import *


async def get_database_instance():
    db = Database(f'postgres://{database["host"]}/{database["db"]}', user=database["user"],
                  password=database["password"])
    await db.connect()
    return db


async def get_all_entries(db: Database, tablename):
    query = "SELECT * FROM %s" % tablename
    return await db.fetch_all(query)


async def get_filtered_entries(db: Database, tablename: str, values: dict = None, orderby: str = None):
    query = "SELECT * FROM %s " % tablename
    if values is not None:
        query += "where %s" % ", ".join(f"{k}='{v}'" for k, v in values.items())
    if orderby is not None:
        query += f"order by {orderby}"
    return await db.fetch_all(query)


async def create_one_entry(db: Database, tablename: str, values: dict):
    query = "INSERT INTO %s(%s) VALUES (:" % (tablename, ", ".join(k for k in values.keys())) + ", :".join(
        k for k in values.keys()) + ")"
    await db.execute(query, values)


async def table_exists(db: Database, tablename: str):
    query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '%s');" % tablename
    data = await db.fetch_one(query)
    return data[0]


async def entry_exists(db: Database, tablename: str, values: dict):
    query_where = " and ".join(f"{k}='{v}'" for k, v in values.items())
    query = "SELECT exists(select 1 FROM %s where %s)" % (tablename, query_where)
    data = await db.fetch_one(query)
    return data[0]


class SHAPassword:
    token = SHAtoken
    encoded_token = token.encode()

    async def create_password(self, password):
        return hashlib.sha256(self.encoded_token + password.encode()).hexdigest()

    async def check_password(self, db, password, username):
        crypted_password = await self.create_password(password)
        return await entry_exists(db, "UserAccount", {"password": crypted_password, "username": username})
