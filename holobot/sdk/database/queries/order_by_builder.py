from .compiled_query import CompiledQuery
from .iquery_part_builder import IQueryPartBuilder
from .limit_builder import LimitBuilder
from .enums import Order
from typing import Any, List, Tuple

class OrderByBuilder(IQueryPartBuilder):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        super().__init__()
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__columns: List[Tuple[str, Order]] = []
    
    def column(self, column_name: str, order: Order = Order.ASCENDING) -> 'OrderByBuilder':
        self.__columns.append((column_name, order))
        return self
    
    def limit(self) -> LimitBuilder:
        return LimitBuilder(self)

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self.__columns) == 0:
            raise ValueError("The ORDER BY clause must have at least one field.")
        
        parent_sql = self.__parent_builder.build()
        sql = [parent_sql[0], "ORDER BY",]
        is_first = True
        for column_name, order in self.__columns:
            if not is_first:
                sql.append(",")
            sql.append(column_name)
            if order == Order.DESCENDING:
                sql.append("DESC")

        return (" ".join(sql), parent_sql[1])
