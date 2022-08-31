from __future__ import annotations

from typing import Any

from .compiled_query import CompiledQuery
from .enums import Order
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .iquery_part_builder import IQueryPartBuilder
from .limit_builder import LimitBuilder

class OrderByBuilder(ICompileableQueryPartBuilder[CompiledQuery]):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        super().__init__()
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__columns: list[tuple[str, Order]] = []

    def column(self, column_name: str, order: Order = Order.ASCENDING) -> OrderByBuilder:
        self.__columns.append((column_name, order))
        return self

    def limit(self) -> LimitBuilder:
        return LimitBuilder(self)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        if not self.__columns:
            raise ValueError("The ORDER BY clause must have at least one field.")

        parent_sql, parent_args = self.__parent_builder.build()
        sql = [parent_sql, "ORDER BY"]
        is_first = True
        for column_name, order in self.__columns:
            if not is_first:
                sql.append(", ")
            sql.append(column_name)
            if order is Order.DESCENDING:
                sql.append("DESC")
            is_first = False

        return (" ".join(sql), parent_args)
