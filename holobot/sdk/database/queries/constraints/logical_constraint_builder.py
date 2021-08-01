from .iconstraint_builder import IConstraintBuilder
from ..enums import Connector
from typing import Any, Tuple

class LogicalConstraintBuilder(IConstraintBuilder):
    def __init__(self, connector: Connector, constraint1: IConstraintBuilder, constraint2: IConstraintBuilder) -> None:
        self.__connector: Connector = connector
        self.__constraint1: IConstraintBuilder = constraint1
        self.__constraint2: IConstraintBuilder = constraint2
    
    @property
    def connector(self) -> Connector:
        return self.__connector
    
    @property
    def constraint1(self) -> IConstraintBuilder:
        return self.__constraint1
    
    @property
    def constraint2(self) -> IConstraintBuilder:
        return self.__constraint2

    def build(self, base_param_index: int) -> Tuple[str, Tuple[Any, ...]]:
        sql = []
        arguments = []

        child_sql, child_args = self.constraint1.build(base_param_index)
        sql.append(child_sql)
        arguments.extend(child_args)
        base_param_index = base_param_index + len(child_args)

        if self.__connector == Connector.OR:
            sql.append("OR")
        else: sql.append("AND")
        
        child_sql, child_args = self.constraint2.build(base_param_index)
        sql.append(child_sql)
        arguments.extend(child_args)

        return (
            "({})".format(" ".join(sql)),
            tuple(arguments)
        )

def and_expression(constraint1: IConstraintBuilder, constraint2: IConstraintBuilder) -> LogicalConstraintBuilder:
    return LogicalConstraintBuilder(Connector.AND, constraint1, constraint2)

def or_expression(constraint1: IConstraintBuilder, constraint2: IConstraintBuilder) -> LogicalConstraintBuilder:
    return LogicalConstraintBuilder(Connector.OR, constraint1, constraint2)
