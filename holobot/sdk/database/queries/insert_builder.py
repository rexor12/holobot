from __future__ import annotations

from typing import Any

from .compiled_query import CompiledQuery
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .on_conflict_builder import OnConflictBuilder
from .returning_builder import ReturningBuilder

class InsertBuilder(ICompileableQueryPartBuilder[CompiledQuery]):
    def __init__(self) -> None:
        self.__table_name: str = ""
        self.__fields: dict[str, Any | None] = {}

    @property
    def table_name(self) -> str:
        return self.__table_name

    @property
    def set_fields(self) -> dict[str, Any | None]:
        return self.__fields

    def in_table(self, table_name: str) -> InsertBuilder:
        self.__table_name = table_name
        return self

    def field(self, column_name: str, value: Any | None) -> InsertBuilder:
        self.__fields[column_name] = value
        return self

    def fields(self, field: tuple[str, Any | None], *fields: tuple[str, Any | None]) -> InsertBuilder:
        self.__fields[field[0]] = field[1]
        self.__fields |= fields
        return self

    def on_conflict(self, column: str, *columns: str) -> OnConflictBuilder:
        return OnConflictBuilder(self, column, *columns)

    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        if not self.__fields:
            raise ValueError("The UPDATE clause must have at least one field.")

        sql = (
            f"INSERT INTO {self.__table_name} "
            f"({', '.join(self.__fields)}) VALUES "
            f"({', '.join(f'${index + 1}' for index in range(len(self.__fields)))})"
        )
        return (sql, tuple(self.__fields.values()))
