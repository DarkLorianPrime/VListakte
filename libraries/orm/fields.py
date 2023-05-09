import datetime
from typing import Type, Literal, Any, Union
from uuid import UUID


class FieldException(Exception):
    pass


class Field:
    name = ""
    var_name = ""
    owner = ""
    field_type: Type[Any]

    def __init__(self, primary_key: bool = False, max_length: int = 256, default: Any = None):
        self.primary = primary_key
        self.max_length = max_length
        self.default = None

    def __set_name__(self, owner, name):
        self.owner = owner
        self.var_name = name

    def __generate_query(self, symbols, other):
        name = self.owner.tablename or self.owner.__name__
        if not isinstance(other, self.field_type):
            param_type = f"Passed type: {type(other).__name__}"
            field_type = f"Expected type: {self.field_type.__name__}"
            raise FieldException(f"Field type and param type not equal!\n{param_type}\n{field_type}")

        if isinstance(other, str):
            other = f"{other}"

        return [f'"{name.lower()}"."{self.var_name}" {symbols} :{self.var_name}', {self.var_name: other}]

    def __eq__(self, other):
        return self.__generate_query("=", other)

    def __ne__(self, other):
        return self.__generate_query("!=", other)

    def __lt__(self, other):
        return self.__generate_query("<", other)

    def __gt__(self, other):
        return self.__generate_query(">", other)

    def __le__(self, other):
        return self.__generate_query("<=", other)

    def __ge__(self, other):
        return self.__generate_query(">=", other)


class StringField(Field):
    name = "varchar"
    field_type = str


class IntegerField(Field):
    name = "integer"
    field_type = int


class BooleanField(Field):
    name = "boolean"
    field_type = bool


class UUIDField(Field):
    name = "uuid"
    field_type = Union[str, UUID]


class DateTimeField(Field):
    name = "timestamptz"
    field_type = datetime.datetime


class TextField(Field):
    name = "text"
    field_type = str


class SerialField(Field):
    name = "serial"
    field_type = int


class Relate(Field):
    name = "..."
    field_type = None


class TimestampField(Field):
    name = "timestamp"
    field_type = datetime.datetime


def _or(string_param):
    return f" OR {string_param}"
