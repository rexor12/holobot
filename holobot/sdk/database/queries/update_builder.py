from .iquery_part_builder import IQueryPartBuilder
from .returning_builder import ReturningBuilder
from .where_builder import WhereBuilder
from typing import Any, Dict, Optional, Tuple

class UpdateBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        self.__table_name: str = ""
        self.__fields: Dict[str, Optional[Any]] = {}

    @property
    def table_name(self) -> str:
        return self.__table_name

    @property
    def set_fields(self) -> Dict[str, Optional[Any]]:
        return self.__fields

    def table(self, table_name: str) -> 'UpdateBuilder':
        self.__table_name = table_name
        return self

    def field(self, column_name: str, value: Optional[Any]) -> 'UpdateBuilder':
        self.__fields[column_name] = value
        return self
    
    def fields(self, field: Tuple[str, Optional[Any]], *fields: Tuple[str, Optional[Any]]) -> 'UpdateBuilder':
        self.__fields[field[0]] = field[1]
        for f in fields:
            self.__fields[f[0]] = f[1]
        return self

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)
    
    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self.__fields) == 0:
            raise ValueError("The UPDATE clause must have at least one field.")

        sql = ["UPDATE", self.__table_name, "SET ("]
        columns = []
        arguments = []
        for column, value in self.__fields.items():
            columns.append(column)
            arguments.append(value)
        sql.append(", ".join(columns))
        sql.append(") = (")
        sql.append(", ".join([f"${index}" for index in range(1, len(arguments) + 1)]))
        sql.append(")")
        return (" ".join(sql), tuple(arguments))
