import inspect


class Field:
    def __init__(self, default=None, max_length=None, null=False):
        self.default = " DEFAULT '{}'".format(default) if default is not None else ""
        if isinstance(default, str):
            self.default = " DEFAULT {}".format(default) if default is not None else ""
        self.max_length = '({})'.format(max_length) if max_length is not None else ''
        self.null = ' NOT NULL' if null else ''


class Text(Field):
    def __init__(self, default=None):
        super().__init__(default)

    def __repr__(self):
        return "text"


class ForeignKey(Field):
    def __init__(self, from_relationship):
        super().__init__()
        self.from_relationship = from_relationship

    def __repr__(self):
        return f"INTEGER references {self.from_relationship.Meta.table_name}(id)"


class String(Field):
    def __init__(self, default=None, max_length=None, null=False):
        super().__init__(default, max_length, null)

    def __repr__(self):
        return f"varchar{self.max_length}{self.default}{self.null}"


class Integer(Field):
    def __repr__(self):
        return "integer"


class UUID(Field):
    def __repr__(self):
        return "uuid"


class Timestamp(Field):
    def __init__(self, default=None):
        super().__init__(default)

    def __repr__(self):
        return f"timestamp {self.default}"


class Boolean(Field):
    def __init__(self, default=None):
        super().__init__(default)

    def __repr__(self):
        print(self.default)
        return f"bool {self.default}"


class ManyToMany(Field):
    def __init__(self, from_relationship=None):
        super().__init__()
        stack = inspect.stack()
        self.from_relationship = from_relationship.Meta.table_name
        self.to_relationship = stack[1][0].f_code.co_name
        self.name = f"{self.from_relationship}_{self.to_relationship}"

    def __repr__(self):
        return f"""CREATE TABLE IF NOT EXISTS {self.name}({self.from_relationship}_id INTEGER references {self.from_relationship}(id), {self.to_relationship}_id INTEGER references {self.to_relationship}(id))"""
