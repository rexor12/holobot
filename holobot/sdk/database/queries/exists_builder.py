from typing import Any

from .compiled_query import CompiledQuery
from .iquery_part_builder import IQueryPartBuilder

class ExistsBuilder(IQueryPartBuilder):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        parent_sql, parent_args = self.__parent_builder.build()
        return (
            " ".join(("SELECT EXISTS (", parent_sql, ")")),
            parent_args
        )
