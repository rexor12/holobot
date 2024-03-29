from __future__ import annotations

from typing import Any

from .compiled_query import CompiledQuery
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .iquery_part_builder import IQueryPartBuilder

class ReturningBuilder(IQueryPartBuilder):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        super().__init__()
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__columns: list[str] = []

    def column(self, column_name: str) -> ReturningBuilder:
        if column_name not in self.__columns:
            self.__columns.append(column_name)
        return self

    def columns(self, column_name: str, *column_names: str) -> ReturningBuilder:
        columns = [column_name, *column_names]
        for column in columns:
            if column not in self.__columns:
                self.__columns.append(column)
        return self

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        if not self.__columns:
            raise ValueError("The RETURNING clause must have at least one field.")

        parent_sql, parent_args = self.__parent_builder.build()
        sql = f"{parent_sql} RETURNING {', '.join(self.__columns)}"
        return (sql, parent_args)
