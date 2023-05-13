from typing import Any

from .compiled_query import CompiledQuery
from .enums import Order
from .iquery_part_builder import IQueryPartBuilder
from .isupports_pagination import ISupportsPagination
from .limit_builder import LimitBuilder
from .order_by_builder import OrderByBuilder
from .paginate_builder import PaginateBuilder
from .returning_builder import ReturningBuilder
from .where_builder import WhereBuilder

class FunctionBuilder(IQueryPartBuilder, ISupportsPagination):
    def __init__(
        self,
        parent_builder: IQueryPartBuilder,
        function_name: str,
        arguments: tuple[str, ...]
    ) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__function_name = function_name
        self.__arguments = arguments

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)

    def order_by(self) -> OrderByBuilder:
        return OrderByBuilder(self)

    def limit(self) -> LimitBuilder:
        return LimitBuilder(self)

    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

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
        parent_sql, parent_args = self.__parent_builder.build()
        function_args = ", ".join(self.__arguments)
        sql = f"{parent_sql} {self.__function_name}({function_args})"

        return (sql, parent_args)
