from typing import List

from databases.backends.postgres import Record


def serializer(records: List[Record], limit: int = None, offset: int = None, need_columns: list = None):
    values = []

    records = records if len(records) == 1 or not limit or offset is None else records[offset:limit]

    for record in records:
        temp_dict = {}

        for key, value in dict(record).items():
            if not need_columns:
                temp_dict[key] = str(value)
                continue
            if key in need_columns:
                temp_dict[key] = str(value)

        values.append(temp_dict)
    return values
