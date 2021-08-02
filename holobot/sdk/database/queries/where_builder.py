from .compiled_query import CompiledQuery
from .iquery_part_builder import IQueryPartBuilder
from .iwhere_builder import IWhereBuilder
from .limit_builder import LimitBuilder
from .returning_builder import ReturningBuilder
from .where_constraint_builder import WhereConstraintBuilder
from .constraints import ColumnConstraintBuilder, EmptyConstraintBuilder, IConstraintBuilder
from .enums import Equality
from typing import Any, Optional, Tuple

class WhereBuilder(IWhereBuilder):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.constraint = EmptyConstraintBuilder()
    
    def field(self, column_name: str, equality: Equality, value: Optional[Any]) -> WhereConstraintBuilder:
        self.constraint = ColumnConstraintBuilder(column_name, equality, value)
        return WhereConstraintBuilder(self)
    
    def expression(self, constraint: IConstraintBuilder) -> WhereConstraintBuilder:
       self.constraint = constraint
       return WhereConstraintBuilder(self)
    
    def limit(self) -> LimitBuilder:
        return LimitBuilder(self)
    
    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if isinstance(self.constraint, EmptyConstraintBuilder):
            raise ValueError("A constraint must be specified.")

        parent_sql = self.__parent_builder.build()
        sql = [parent_sql[0], "WHERE"]
        arguments = list(parent_sql[1])

        constraint_sql, constraint_args = self.constraint.build(len(arguments) + 1)
        sql.append(constraint_sql)
        arguments.extend(constraint_args)

        return (" ".join(sql), tuple(arguments))
