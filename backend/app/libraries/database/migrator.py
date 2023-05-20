from libraries.orm.core import Model
from libraries.orm.database import db
from libraries.orm.fields import SerialField, TextField, TimestampField


class Migrations(Model):
    id = SerialField()
    name = TextField()
    timestamp = TimestampField()

    @classmethod
    async def table_exists(cls):
        query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'migrations')"
        return await db.execute(query)

    @classmethod
    async def entry_exists(cls, **values):
        query_where = ", ".join(f"{k}='{v}'" for k, v in values.items())
        query = "SELECT exists(select 1 FROM \"migrations\" where %s)" % (query_where,)
        return await db.execute(query)