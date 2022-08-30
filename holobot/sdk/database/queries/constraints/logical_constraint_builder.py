from typing import Any

from ..enums import Connector
from .iconstraint_builder import IConstraintBuilder

class LogicalConstraintBuilder(IConstraintBuilder):
    def __init__(
        self,
        connector: Connector,
        constraint1: IConstraintBuilder,
        constraint2: IConstraintBuilder,
        *constraints: IConstraintBuilder
    ) -> None:
        self.__connector: Connector = connector
        self.__constraints: tuple[IConstraintBuilder, ...] = tuple([constraint1, constraint2, *constraints])

    @property
    def connector(self) -> Connector:
        return self.__connector

    @property
    def constraints(self) -> tuple[IConstraintBuilder, ...]:
        return self.__constraints

    def build(self, base_param_index: int) -> tuple[str, tuple[Any, ...]]:
        sql = []
        arguments = []

        is_first_constraint = True
        for constraint in self.__constraints:
            if not is_first_constraint:
                sql.append("OR" if self.__connector is Connector.OR else "AND")

            child_sql, child_args = constraint.build(base_param_index)
            sql.append(child_sql)
            arguments.extend(child_args)
            base_param_index = base_param_index + len(child_args)
            is_first_constraint = False

        return (f"({' '.join(sql)})", tuple(arguments))

def and_expression(
    constraint1: IConstraintBuilder,
    constraint2: IConstraintBuilder,
    *constraints: IConstraintBuilder
) -> LogicalConstraintBuilder:
    return LogicalConstraintBuilder(Connector.AND, constraint1, constraint2, *constraints)

def or_expression(
    constraint1: IConstraintBuilder,
    constraint2: IConstraintBuilder,
    *constraints: IConstraintBuilder
) -> LogicalConstraintBuilder:
    return LogicalConstraintBuilder(Connector.OR, constraint1, constraint2, *constraints)
