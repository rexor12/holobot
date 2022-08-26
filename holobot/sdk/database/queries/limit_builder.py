from __future__ import annotations

from typing import Any

from .compiled_query import CompiledQuery
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .iquery_part_builder import IQueryPartBuilder

class LimitBuilder(ICompileableQueryPartBuilder[CompiledQuery]):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        super().__init__()
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__start_index: int | None = None
        self.__max_count: int | None = None

    def max_count(self, max_count: int) -> LimitBuilder:
        self.__max_count = max_count
        return self

    def start_index(self, start_index: int) -> LimitBuilder:
        self.__start_index = start_index
        return self

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        if self.__start_index is None and self.__max_count is None:
            raise ValueError("The LIMIT clause must have either an offset or a maximum count.")

        parent_sql, parent_args = self.__parent_builder.build()
        sql = [parent_sql]
        arguments = list(parent_args)
        if self.__max_count is not None:
            sql.append("LIMIT")
            sql.append(f"${len(arguments) + 1}")
            arguments.append(self.__max_count)
        if self.__start_index is not None:
            sql.append("OFFSET")
            sql.append(f"${len(arguments) + 1}")
            arguments.append(self.__start_index)

        return (" ".join(sql), tuple(arguments))
