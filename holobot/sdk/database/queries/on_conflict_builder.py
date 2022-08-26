from typing import Any

from .compiled_query import CompiledQuery
from .do_nothing_builder import DoNothingBuilder
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .iquery_part_builder import IQueryPartBuilder
from .on_conflict_update_builder import OnConflictUpdateBuilder

class OnConflictBuilder(ICompileableQueryPartBuilder[CompiledQuery]):
    def __init__(self, parent_builder: IQueryPartBuilder, column: str, *columns: str) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__columns: list[str] = [column, *columns]

    def do_nothing(self) -> DoNothingBuilder:
        return DoNothingBuilder(self)

    def update(self) -> OnConflictUpdateBuilder:
        return OnConflictUpdateBuilder(self)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        parent_sql, arguments = self.__parent_builder.build()
        sql = [parent_sql, "ON CONFLICT (", ", ".join(self.__columns), ") DO"]
        return (" ".join(sql), tuple(arguments))
