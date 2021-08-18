from .iquery_part_builder import IQueryPartBuilder
from .returning_builder import ReturningBuilder
from .where_builder import WhereBuilder
from typing import Any, Dict, Optional, Tuple

class UpdateBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        self.__table_name: str = ""
        self.__fields: Dict[str, Tuple[Optional[Any], bool]] = {}

    @property
    def table_name(self) -> str:
        return self.__table_name

    @property
    def set_fields(self) -> Dict[str, Optional[Any]]:
        return self.__fields

    def table(self, table_name: str) -> 'UpdateBuilder':
        self.__table_name = table_name
        return self

    def field(self, column_name: str, value: Optional[Any], is_raw_value: bool = False) -> 'UpdateBuilder':
        self.__fields[column_name] = (value, is_raw_value)
        return self
    
    def fields(self, field: Tuple[str, Optional[Any]], *fields: Tuple[str, Optional[Any]]) -> 'UpdateBuilder':
        self.__fields[field[0]] = (field[1], False)
        for f in fields:
            self.__fields[f[0]] = (f[1], False)
        return self

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)
    
    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self.__fields) == 0:
            raise ValueError("The UPDATE clause must have at least one field.")

        sql = ["UPDATE", self.__table_name, "SET"]
        arguments = []
        columns = []
        if len(self.__fields) > 1:
            sql.append("(")
            for column in self.__fields.keys():
                columns.append(column)
            sql.append(", ".join(columns))
            sql.append(") = (")
            is_first_value = True
            index = 1
            for value, is_raw_value in self.__fields.values():
                if not is_first_value:
                    sql.append(", ")
                is_first_value = False
                if not is_raw_value:
                    sql.append(f"${index}")
                    arguments.append(value)
                    index = index + 1
                else: sql.append(str(value))
            sql.append(")")
        else:
            column, value = next(iter(self.__fields.items()))
            sql.append(column)
            sql.append("=")
            if not value[1]:
                sql.append("$1")
                arguments.append(value[0])
            else: sql.append(str(value[0]))
        return (" ".join(sql), tuple(arguments))
