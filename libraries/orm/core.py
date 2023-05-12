import asyncio
import re
from typing import Literal, List, Optional

from databases.backends.postgres import Record

from libraries.orm.database import db


class Query:
    _end_query = ""
    _query = []
    _order = ""

    def __init__(self, model_name, query=None):
        self.group = ""
        self.result = None
        self._query = []
        if query is not None:
            self._query.extend(query)

        self._model_name = model_name.lower()
        self._order = ""
        asyncio.create_task(self._generate_query())

    async def _generate_query(self):
        self._end_query = f"select * from \"{self._model_name}\" "
        self._end_query += self._get_where()
        self._end_query += self._order
        self._end_query += self.group
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
            params = list(map(lambda param: f"\"{param}\"" if "count" not in param else param, params))
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
            self._end_query += f" offset {item.start}"

        if item.stop is not None:
            self._end_query += f" limit {item.stop}"

        result = await db.fetch_all(self._end_query)
        if result is None:
            return None

        self.result = result
        return list(result)

    def __getitem__(self, item):
        result = asyncio.run(self.async_getitem(item))
        return result

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
        await db.execute(f"DELETE FROM {self._model_name} {where}", self._where_params)
        return self

    async def insert(self, *returned, **kwargs):
        values = ", ".join(kwargs.keys())
        values_dot = ":" + values.replace(" ", " :")
        if not returned:
            return await db.execute(f"INSERT INTO {self._model_name}({values}) VALUES ({values_dot})", kwargs)

        fields = ", ".join(returned)
        return await db.fetch_one(f"INSERT INTO {self._model_name}"
                                  f"({values}) VALUES ({values_dot}) RETURNING {fields}", kwargs)

    async def insert_many(self, parameters, *returned, ) -> List[Record]:
        insert_dict = {}
        values_keys = ", ".join(parameters[0].keys())
        insert_queries = []

        for num, values in enumerate(parameters):
            values_dot = ", ".join(f":{k}_{num}" for k in values.keys())
            insert_dict.update({f"{k}_{num}": v for k, v in values.items()})
            insert_queries.append(f"({values_dot})")

        values_values = ", ".join(insert_queries)

        query = f"INSERT INTO {self._model_name}({values_keys}) VALUES {values_values}"

        if returned:
            fields = ", ".join(returned)
            query += f" RETURNING {fields}"
            return await db.fetch_all(query, insert_dict)

        return await db.execute(query, insert_dict)

    def group_by(self, *fields):
        self.group = f" group by {', '.join(fields)}"
        return self

    async def update(self, values: dict) -> Optional[Record]:
        where = self._get_where()
        updated = ", ".join(f"\"{k}\"=:{k}" for k, v in values.items())
        query = f"UPDATE {self._model_name} SET {updated} {where}"
        values.update(self._where_params)
        return await db.execute(query, values)


def __iter__(self):
    return iter(self.result)


class Model:
    query = ""
    tablename = ""

    @classmethod
    def objects(cls):
        name = cls.tablename or cls.__name__
        return Query(name)

    @classmethod
    def filter(cls, *queries):
        name = cls.tablename or cls.__name__
        return Query(name.lower(), queries)
