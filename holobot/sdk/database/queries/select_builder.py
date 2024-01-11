from __future__ import annotations

from typing import Any

from .compiled_query import CompiledQuery
from .enums import Order
from .exists_builder import ExistsBuilder
from .function_builder import FunctionBuilder
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .join_builder import JOIN_TYPE, JoinBuilder
from .paginate_builder import PaginateBuilder
from .isupports_pagination import ISupportsPagination
from .where_builder import WhereBuilder

class SelectBuilder(ICompileableQueryPartBuilder[CompiledQuery], ISupportsPagination):
    def __init__(self) -> None:
        super().__init__()
        self.__columns: list[str] = []
        self.__table_name: str | None = None
        self.__table_alias: str | None = None
        self.__is_count_select: bool = False
        self.__has_from_part: bool = False

    def column(self, column_name: str) -> SelectBuilder:
        if column_name in self.__columns:
            return self

        self.__columns.append(column_name)
        return self

    def columns(self, *column_names: str) -> SelectBuilder:
        for column_name in column_names:
            self.column(column_name)
        return self

    def count(self) -> SelectBuilder:
        self.__is_count_select = True
        return self

    def from_table(self, table_name: str, alias: str | None = None) -> SelectBuilder:
        self.__table_name = table_name
        self.__table_alias = alias
        self.__has_from_part = True
        return self

    def from_function(self, function_name: str, arguments: tuple[str, ...]) -> FunctionBuilder:
        self.__has_from_part = True
        return FunctionBuilder(self, function_name, arguments)

    def join(
        self,
        table_name: str,
        left_column: str,
        right_column: str,
        alias: str | None = None,
        join_type: JOIN_TYPE = "LEFT"
    ) -> JoinBuilder:
        return JoinBuilder(self, table_name, left_column, right_column, alias, join_type)

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)

    def exists(self) -> ExistsBuilder:
        return ExistsBuilder(self)

    def paginate(
        self,
        ordering_columns: tuple[tuple[str, Order], ...],
        page_index: int,
        page_size: int
    ) -> PaginateBuilder:
        return PaginateBuilder(self, ordering_columns, page_index, page_size)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        if not self.__columns and not self.__is_count_select:
            raise ValueError("At least one column must be specified.")

        sql = ["SELECT", "COUNT(*)" if self.__is_count_select else ", ".join(self.__columns)]

        if self.__has_from_part:
            sql.append("FROM")

        if self.__table_name:
            sql.append(self.__table_name)
            if self.__table_alias:
                sql.extend(("AS", self.__table_alias))

        return (" ".join(sql), ())
