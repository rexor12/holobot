from __future__ import annotations

from typing import Any

from .iquery_part_builder import IQueryPartBuilder
from .where_builder import WhereBuilder

class DeleteBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.__table_name: str | None = None
        self.__schema_name: str | None = None

    def from_table(
        self,
        table_name: str,
        schema_name: str | None = None
    ) -> DeleteBuilder:
        self.__table_name = table_name
        self.__schema_name = schema_name
        return self

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)

    def build(self) -> tuple[str, tuple[Any, ...]]:
        if not self.__table_name:
            raise ValueError("The source table must be specified.")

        sql_parts = ["DELETE FROM "]
        if self.__schema_name:
            sql_parts.append(self.__schema_name)
            sql_parts.append(".")

        sql_parts.append(self.__table_name)

        return ("".join(sql_parts), ())
