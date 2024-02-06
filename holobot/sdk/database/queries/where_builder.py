from collections.abc import Sequence
from typing import Any, TypeVar

from .compiled_query import CompiledQuery
from .constraints import (
    ColumnConstraintBuilder, ColumnInConstraintBuilder, EmptyConstraintBuilder, IConstraintBuilder,
    LogicalConstraintBuilder
)
from .enums import Connector, Equality, Order
from .exists_builder import ExistsBuilder
from .iquery_part_builder import IQueryPartBuilder
from .isupports_pagination import ISupportsPagination
from .iwhere_builder import IWhereBuilder
from .limit_builder import LimitBuilder
from .order_by_builder import OrderByBuilder
from .paginate_builder import PaginateBuilder
from .returning_builder import ReturningBuilder
from .where_constraint_builder import WhereConstraintBuilder

T = TypeVar("T")

class WhereBuilder(IWhereBuilder, ISupportsPagination):
    @property
    def constraint(self) -> IConstraintBuilder:
        return self.__constraint

    @constraint.setter
    def constraint(self, value: IConstraintBuilder) -> None:
        self.__constraint = value

    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.constraint = EmptyConstraintBuilder()

    def field(
        self,
        column_name: str,
        equality: Equality,
        value: Any | None,
        is_raw_value: bool = False
    ) -> WhereConstraintBuilder:
        self.constraint = ColumnConstraintBuilder(column_name, equality, value, is_raw_value)
        return WhereConstraintBuilder(self)

    def fields(
        self,
        connector: Connector,
        field1: tuple[str, Equality, Any | None],
        field2: tuple[str, Equality, Any | None],
        *fields: tuple[str, Equality, Any | None]
    ) -> WhereConstraintBuilder:
        self.constraint = LogicalConstraintBuilder(
            connector,
            ColumnConstraintBuilder(field1[0], field1[1], field1[2]),
            ColumnConstraintBuilder(field2[0], field2[1], field2[2]),
            *[ColumnConstraintBuilder(field[0], field[1], field[2]) for field in fields]
        )
        return WhereConstraintBuilder(self)

    def field_in(
        self,
        column_name: str,
        values: Sequence[T] # type: ignore
    ) -> WhereConstraintBuilder:
        self.constraint = ColumnInConstraintBuilder(column_name, values)
        return WhereConstraintBuilder(self)

    def expression(self, constraint: IConstraintBuilder) -> WhereConstraintBuilder:
        self.constraint = constraint
        return WhereConstraintBuilder(self)

    def order_by(self) -> OrderByBuilder:
        return OrderByBuilder(self)

    def limit(self) -> LimitBuilder:
        return LimitBuilder(self)

    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

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
        if isinstance(self.constraint, EmptyConstraintBuilder):
            raise ValueError("A constraint must be specified.")

        parent_sql, parent_args = self.__parent_builder.build()
        constraint_sql, constraint_args = self.constraint.build(len(parent_args) + 1)
        sql = f"{parent_sql} WHERE {constraint_sql}"

        return (sql, parent_args + constraint_args)
