import hashlib
import os
from typing import Union

import dotenv
from databases import Database

from libraries.utils.extra_features import Singleton
from colorama import Fore

dotenv.load_dotenv("libraries/.env")


class DatabaseORM(Singleton):
    __host = os.getenv("host")
    __database = os.getenv("db")
    __user = os.getenv("user")
    __password = os.getenv("password")
    db = Database(f'postgres://{__host}/{__database}', user=__user, password=__password)

    def is_connected(self) -> bool:
        return self.db.is_connected

    async def connect(self) -> None:
        await self.db.connect()

    async def disconnect(self) -> None:
        await self.db.disconnect()

    async def get_all_entries(self, table_name: str) -> list:
        """
        :param table_name: имя таблицы взаимодействия
        :return: список найденных объектов
        """
        query = "SELECT * FROM %s" % table_name
        return await self.db.fetch_all(query)

    async def get_filtered_entries(self, table_name: str, where: dict = None, order_by: str = None) -> list:
        """
        :param table_name: имя таблицы взаимодействия
        :param where: значения объекта взаимодействия (название столбца: значение)
        :param order_by: сортировка объекта (название столбца)
        :return: список найденных объектов
        """
        query = "SELECT * FROM %s " % table_name
        if where is not None:
            query += "where %s" % " and ".join(f"{k}='{v}'" for k, v in values.items())
        if order_by is not None:
            query += f"order by {order_by}"
        return await self.db.fetch_all(query)

    async def create_one_entry(self, table_name: str, values: dict) -> None:
        """
        :param table_name: имя таблицы взаимодействия
        :param values: значения объекта взаимодействия (название столбца: значение)
        """
        values_str = ":" + ", :".join(k for k in values.keys())
        values_name = ", ".join(k for k in values.keys())
        query = "INSERT INTO %s(%s) VALUES (%s" % (table_name, values_name, values_str) + ")"
        await self.db.execute(query, values)

    async def table_exists(self, table_name: str) -> bool:
        """
        :param table_name: имя таблицы взаимодействия
        :return: Существует ли таблица с заданным названием
        """
        query = "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '%s');" % table_name.lower()
        data = await self.db.fetch_one(query)
        return data[0]

    async def create_many_entries(self, table_name: str, values: list) -> None:
        """
        :param table_name: имя таблицы взаимодействия
        :param values: значения которые будут постепенно внесены (список со словарями внутри)
        :return: recursion | None
        """
        if len(values) == 0:
            return
        await self.create_one_entry(table_name=table_name, values=values[0])
        values.pop(0)
        return await self.create_many_entries(table_name=table_name, values=values)

    async def entry_exists(self, table_name: str, where: dict) -> bool:
        """
        Проверяет, существует ли запись
        :param table_name: имя таблицы взаимодействия
        :param where: поля поиска объекта, который нужно проверить на существование (название столбца: значение)
        :return: True | False, существует ли запись
        """
        query_where = " and ".join(f"{k}='{v}'" for k, v in where.items())
        query = "SELECT exists(select 1 FROM %s where %s)" % (table_name, query_where)
        data = await self.db.fetch_one(query)
        return data[0]

    async def update(self, table_name: str, values: Union[list, dict], where: dict) -> None:
        """
        Обновляет существующие значения записи
        :param table_name: имя таблицы взаимодействия
        :param where: поля поиска объекта, который нужно обновить (название столбца: значение)
        :param values: значения, которые будут обновлены
        """
        query_many_set = ""
        if type(values) == list:
            query_many_set = ", ".join([next(f"{k}='{v}'" for k, v in value.items()) for value in values])
        if type(values) == dict:
            query_many_set = [f'{key} = ' + ', '.join(f'{z} ' for z in value) for key, value in values.items()]
        query_where = " and ".join(f"{k}='{v}'" for k, v in where.items())
        query_many_set = ''.join(query_many_set)
        query = "UPDATE %s SET %s WHERE %s" % (table_name, query_many_set, query_where)
        await self.db.fetch_one(query)

    async def delete(self, table_name: str, where: dict) -> None:
        """
        Удаляет запись с переданными параметрами
        :param table_name: имя таблицы взаимодействия
        :param where: поля поиска записи, которую нужно удалить (название столбца: значение)
        """
        query_where = " and ".join(f"{k}='{v}'" for k, v in where.items())
        await self.db.fetch_one("DELETE FROM %s where %s" % (table_name, query_where))


class SHAPassword:
    def __init__(self, table_name: str) -> None:
        """
        получение токена хэширования
        :param table_name: назначение таблицы
        """
        self.encoded_token = "".encode() if os.getenv("SHATOKEN") is None else os.getenv("shatoken").encode()
        self.table = table_name

    async def create_password(self, password: str) -> hex:
        """
        :param password: пароль для шифровки
        :return: зашифрованный пароль
        """
        return hashlib.sha256(self.encoded_token + password.encode()).hexdigest()

    async def check_password(self, password: str, username: str):
        """
        :param password: пароль для сравнения (хэшируется и сравнивается с базой данных)
        :param username: логин для сравнения (кому принадлежит пароль)
        :return: подошел ли пароль / логин
        """
        crypted_password = await self.create_password(password)
        return await DatabaseORM().entry_exists(self.table, {"password": crypted_password, "username": username})
