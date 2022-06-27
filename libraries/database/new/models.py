import asyncio
import inspect
import os
import sys

import dotenv
from databases import Database

from libraries.utils.extra_features import Singleton
import importlib

class Query:
    pass


class Model:
    pass


dotenv.load_dotenv()


class DatabaseORM(Singleton):
    __host = os.getenv("host")
    __database = os.getenv("db")
    __user = os.getenv("user")
    __password = os.getenv("password")
    db = Database(f'postgres://{__host}/{__database}', user=__user, password=__password)
