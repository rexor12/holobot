from .compiled_query import CompiledQuery
from .do_nothing_builder import DoNothingBuilder
from .iquery_part_builder import IQueryPartBuilder
from .on_conflict_update_builder import OnConflictUpdateBuilder
from typing import Any, List, Tuple

class OnConflictBuilder(IQueryPartBuilder):
    def __init__(self, parent_builder: IQueryPartBuilder, column: str, *columns: str) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__columns: List[str] = [column, *columns]
    
    def do_nothing(self) -> DoNothingBuilder:
        return DoNothingBuilder(self)
    
    def update(self) -> OnConflictUpdateBuilder:
        return OnConflictUpdateBuilder(self)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        parent_sql, arguments = self.__parent_builder.build()
        sql = [parent_sql, "ON CONFLICT (", ", ".join(self.__columns), ") DO"]
        return (" ".join(sql), tuple(arguments))
