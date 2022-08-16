from .compiled_query import CompiledQuery
from .iquery_part_builder import IQueryPartBuilder
from typing import Any

class DoNothingBuilder(IQueryPartBuilder):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        sql, arguments = self.__parent_builder.build()
        return (f"{sql} NOTHING", tuple(arguments))
