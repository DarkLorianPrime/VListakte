import asyncio
import re
from typing import Literal

from libraries.orm.database import db


class Query:
    _end_query = ""
    _query = []
    _order = ""

    def __init__(self, model_name, query=None):
        self.result = None
        self._query = []
        if query is not None:
            self._query.extend(query)

        self._model_name = model_name.lower()
        self._order = ""
        asyncio.create_task(self._generate_query())

    @classmethod
    async def async_init(cls, model_name, query=None):
        self = Query(model_name, query)
        return self

    async def _send_transaction(self):
        pass

    async def _generate_query(self):
        self._end_query = f"select * from \"{self._model_name}\" "
        self._end_query += self._get_where()
        self._end_query += self._order
        return self

    def order_by(self, field, side: Literal["asc", "desc", "DESC", "ASC"]):
        self._order = f" order by {field.var_name} {side}"
        return self

    def all(self):
        return self

    async def values(self, *params):
        await self._generate_query()
        query = self._end_query

        if params:
            params = list(map(lambda param: f"\"{param}\"", params))
            query = query.replace("*", ", ".join(params))

        result = await db.fetch_all(query, self._where_params)
        if result is None:
            return None

        self.result = result
        return list(result)

    async def async_getitem(self, item):
        await self._generate_query()
        if not isinstance(item, slice):
            if isinstance(item, int):
                self._end_query += f" limit 1 offset {item}"
            return self
        if item.start is not None:
            self._end_query += f" limit {item.start}"

        if item.stop is not None:
            self._end_query += f" offset {item.stop}"

        return list(await db.execute(self._end_query))

    def __getitem__(self, item):
        task = asyncio.create_task(self._generate_query())
        return task.result()

    async def count(self):
        self._end_query = re.sub(r"^select (.+) from", 'select count("id") from', self._end_query)
        self._end_query += self._get_where()
        # call
        return self

    def _get_where(self):
        where_params = {}
        [[where_params.update({key: value}) for key, value in param[1].items()] for param in self._query]
        where = "where " + ' and '.join([i[0] for i in self._query if "OR" not in i])
        self._where_params = where_params
        where += ''.join([i[0] for i in self._query if "OR" in i])
        return where if where != "where " else ""

    async def exists(self):
        where = self._get_where()
        query = f"SELECT EXISTS(SELECT 1 FROM {self._model_name} {where});"
        self._end_query = query
        query = await db.fetch_one(query, self._where_params)
        print(print(self._end_query, self._where_params))
        return query.exists

    def filter(self, *queries):
        self._query.extend(queries)
        return self

    async def first(self, *params):
        await self._generate_query()
        query = self._end_query
        if params:
            params = list(map(lambda param: f"\"{param}\"", params))
            query = query.replace("*", ", ".join(params))

        return await db.fetch_one(query, self._where_params)

    async def delete(self):
        where = self._get_where()
        await db.execute(f"delete from {self._model_name} {where}")
        return self

    async def insert(self, *returned, **kwargs):
        values = ", ".join(kwargs.keys())
        values_dot = ":" + values.replace(" ", " :")
        if not returned:
            return await db.execute(f"INSERT INTO {self._model_name}({values}) VALUES ({values_dot})", kwargs)

        fields = ", ".join(returned)
        return await db.fetch_one(f"INSERT INTO {self._model_name}"
                                  f"({values}) VALUES ({values_dot}) RETURNING {fields}", kwargs)

    async def insert_many(self, parameters, *returned,):
        insert_dict = {}
        values = ""
        insert_query = ""
        for num, value in enumerate(parameters):
            values = ", ".join(value.keys())
            values_dot = ":" + values.replace(" ", " :")
            insert_query += f"({values_dot})"
        query = f"INSERT INTO {self._model_name}({values}) VALUES {insert_query}"
        if not returned:
            pass

        fields = ", ".join(returned)
        query += f"RETURNING {fields}"
        print(query)

    def __iter__(self):
        if self.result:
            return iter(self.result)

        return iter(db.fetch_all(self._query))


class Model:
    query = ""
    tablename = ""

    @classmethod
    def objects(cls):
        name = cls.tablename or cls.__name__
        print(name)
        return Query(name)

    @classmethod
    def filter(cls, *queries):
        name = cls.tablename or cls.__name__
        print(name)
        return Query(name.lower(), queries)
