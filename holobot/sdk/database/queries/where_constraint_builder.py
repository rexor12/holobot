from .compiled_query import CompiledQuery
from .iquery_part_builder import IQueryPartBuilder
from .limit_builder import LimitBuilder
from .order_by_builder import OrderByBuilder
from .paginate_builder import PaginateBuilder
from .returning_builder import ReturningBuilder
from .where_builder import IWhereBuilder
from .constraints import ColumnConstraintBuilder, IConstraintBuilder, LogicalConstraintBuilder
from .enums import Connector, Equality
from typing import Any

class WhereConstraintBuilder(IQueryPartBuilder):
    def __init__(self, where_builder: IWhereBuilder) -> None:
        self.__where_builder: IWhereBuilder = where_builder

    def and_field(self, column_name: str, equality: Equality, value: Any | None) -> 'WhereConstraintBuilder':
        return self.__append_constraint(Connector.AND, ColumnConstraintBuilder(column_name, equality, value))

    def or_field(self, column_name: str, equality: Equality, value: Any | None) -> 'WhereConstraintBuilder':
        return self.__append_constraint(Connector.OR, ColumnConstraintBuilder(column_name, equality, value))

    def and_expression(self, constraint: IConstraintBuilder) -> 'WhereConstraintBuilder':
        return self.__append_constraint(Connector.AND, constraint)

    def or_expression(self, constraint: IConstraintBuilder) -> 'WhereConstraintBuilder':
        return self.__append_constraint(Connector.OR, constraint)

    def order_by(self) -> OrderByBuilder:
        return OrderByBuilder(self)

    def limit(self) -> LimitBuilder:
        return LimitBuilder(self)

    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def paginate(
        self,
        ordering_column: str,
        page_index: int,
        page_size: int
    ) -> PaginateBuilder:
        return PaginateBuilder(self, ordering_column, page_index, page_size)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> tuple[str, tuple[Any, ...]]:
        return self.__where_builder.build()

    def __append_constraint(self, connector: Connector, constraint: IConstraintBuilder) -> 'WhereConstraintBuilder':
        # TODO Optimize this to avoid wrapping when the connectors are identical; append instead.
        self.__where_builder.constraint = LogicalConstraintBuilder(
            connector,
            self.__where_builder.constraint,
            constraint
        )
        return self
