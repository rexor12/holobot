from .compiled_query import CompiledQuery
from .iquery_part_builder import IQueryPartBuilder
from typing import Any, List, Tuple

class ReturningBuilder(IQueryPartBuilder):
    def __init__(self, parent_builder: IQueryPartBuilder) -> None:
        super().__init__()
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__columns: List[str] = []
    
    def column(self, column_name: str) -> 'ReturningBuilder':
        if column_name in self.__columns:
            return self
        
        self.__columns.append(column_name)
        return self
    
    def columns(self, column_name: str, *column_names: str) -> 'ReturningBuilder':
        columns = [column_name, *column_names]
        for column in columns:
            if column not in self.__columns:
                self.__columns.append(column)
        return self

    def compile(self) -> CompiledQuery:
        return CompiledQuery(*self.build())

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self.__columns) == 0:
            raise ValueError("The RETURNING clause must have at least one field.")
        
        parent_sql = self.__parent_builder.build()
        sql = [parent_sql[0], "RETURNING", ", ".join(self.__columns)]
        return (" ".join(sql), parent_sql[1])
