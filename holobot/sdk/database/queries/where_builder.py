from .iquery_part_builder import IQueryPartBuilder
from .limit_builder import LimitBuilder
from .returning_builder import ReturningBuilder
from .enums import Connector, Equality
from typing import Any, List, Optional, Tuple

class WhereBuilder(IQueryPartBuilder):
    def __init__(self, parent_builder: IQueryPartBuilder, column_name: str, operation: Equality, value: Optional[Any]) -> None:
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__fields: List[Tuple[Connector, str, Equality, Optional[Any]]] = [(Connector.AND, column_name, operation, value)]
    
    def and_field(self, column_name: str, operation: Equality, value: Optional[Any]) -> 'WhereBuilder':
        self.__fields.append((Connector.AND, column_name, operation, value))
        return self
    
    def or_field(self, column_name: str, operation: Equality, value: Optional[Any]) -> 'WhereBuilder':
        self.__fields.append((Connector.OR, column_name, operation, value))
        return self
    
    def limit(self) -> LimitBuilder:
        return LimitBuilder(self)
    
    def returning(self) -> ReturningBuilder:
        return ReturningBuilder(self)

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self.__fields) == 0:
            raise ValueError("The WHERE clause must have at least one field.")
        
        parent_sql = self.__parent_builder.build()
        sql = [parent_sql[0], "WHERE"]
        arguments = list(parent_sql[1])
        is_first_constraint = True
        for connector, column, operation, value in self.__fields:
            if not is_first_constraint:
                sql.append("AND" if connector == Connector.AND else "OR")
            sql.append(column)
            if value is None:
                if not operation == Equality.EQUAL:
                    raise ValueError(f"The only permitted operation for a NULL value is equality, but got '{operation}'.")
                sql.append("IS NULL")
            elif operation == Equality.EQUAL:
                sql.append("=")
                sql.append(f"${len(arguments) + 1}")
                arguments.append(value)
            is_first_constraint = False
        
        return (" ".join(sql), tuple(arguments))
