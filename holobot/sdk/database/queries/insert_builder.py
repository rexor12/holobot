from .compiled_query import CompiledQuery
from .iquery_part_builder import IQueryPartBuilder
from .returning_builder import ReturningBuilder
from typing import Any, Dict, Optional, Tuple

class InsertBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        self._table_name: str = ""
        self._fields: Dict[str, Optional[Any]] = {}

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def fields(self) -> Dict[str, Optional[Any]]:
        return self._fields

    def in_table(self, table_name: str) -> 'InsertBuilder':
        self._table_name = table_name
        return self

    def field(self, column_name: str, value: Optional[Any]) -> 'InsertBuilder':
        self._fields[column_name] = value
        return self
    
    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self._fields) == 0:
            raise ValueError("The UPDATE clause must have at least one field.")

        sql = ["INSERT INTO", self._table_name, "("]
        columns = []
        arguments = []
        for column, value in self._fields.items():
            columns.append(column)
            arguments.append(value)
        sql.append(", ".join(columns))
        sql.append(") VALUES (")
        sql.append(", ".join([f"${index}" for index in range(1, len(arguments) + 1)]))
        sql.append(")")
        return (" ".join(sql), tuple(arguments))
