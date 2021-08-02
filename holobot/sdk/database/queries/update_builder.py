from .iquery_part_builder import IQueryPartBuilder
from .returning_builder import ReturningBuilder
from .where_builder import WhereBuilder
from typing import Any, Dict, Optional, Tuple

class UpdateBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        self._table_name: str = ""
        self._fields: Dict[str, Optional[Any]] = {}

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def fields(self) -> Dict[str, Optional[Any]]:
        return self._fields

    def table(self, table_name: str) -> 'UpdateBuilder':
        self._table_name = table_name
        return self

    def field(self, column_name: str, value: Optional[Any]) -> 'UpdateBuilder':
        self._fields[column_name] = value
        return self

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)
    
    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self._fields) == 0:
            raise ValueError("The UPDATE clause must have at least one field.")

        sql = ["UPDATE", self._table_name, "SET ("]
        columns = []
        arguments = []
        for column, value in self._fields.items():
            columns.append(column)
            arguments.append(value)
        sql.append(", ".join(columns))
        sql.append(") = (")
        sql.append(", ".join([f"${index}" for index in range(1, len(arguments) + 1)]))
        sql.append(")")
        return (" ".join(sql), tuple(arguments))
