from .compiled_query import CompiledQuery
from .iquery_part_builder import IQueryPartBuilder
from .returning_builder import ReturningBuilder
from typing import Any, Dict, Optional, Tuple

class InsertBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        self.__table_name: str = ""
        self.__fields: Dict[str, Optional[Any]] = {}

    @property
    def table_name(self) -> str:
        return self.__table_name

    @property
    def set_fields(self) -> Dict[str, Optional[Any]]:
        return self.__fields

    def in_table(self, table_name: str) -> 'InsertBuilder':
        self.__table_name = table_name
        return self

    def field(self, column_name: str, value: Optional[Any]) -> 'InsertBuilder':
        self.__fields[column_name] = value
        return self
    
    def fields(self, field: Tuple[str, Optional[Any]], *fields: Tuple[str, Optional[Any]]) -> 'InsertBuilder':
        self.__fields[field[0]] = field[1]
        for f in fields:
            self.__fields[f[0]] = f[1]
        return self
    
    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self.__fields) == 0:
            raise ValueError("The UPDATE clause must have at least one field.")

        sql = ["INSERT INTO", self.__table_name, "("]
        columns = []
        arguments = []
        for column, value in self.__fields.items():
            columns.append(column)
            arguments.append(value)
        sql.append(", ".join(columns))
        sql.append(") VALUES (")
        sql.append(", ".join([f"${index}" for index in range(1, len(arguments) + 1)]))
        sql.append(")")
        return (" ".join(sql), tuple(arguments))
