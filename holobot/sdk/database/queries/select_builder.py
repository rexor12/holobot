from .iquery_part_builder import IQueryPartBuilder
from .where_builder import WhereBuilder
from typing import Any, List, Optional, Tuple

class SelectBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.__columns: List[str] = []
        self.__table_name: Optional[str] = None
        self.__is_count_select: bool = False
    
    def column(self, column_name: str) -> 'SelectBuilder':
        if column_name in self.__columns:
            return self
        
        self.__columns.append(column_name)
        return self
    
    def columns(self, *column_names: str) -> 'SelectBuilder':
        for column_name in column_names:
            self.column(column_name)
        return self
    
    def count(self) -> 'SelectBuilder':
        self.__is_count_select = True
        return self
    
    def from_table(self, table_name: str) -> 'SelectBuilder':
        self.__table_name = table_name
        return self

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self.__columns) == 0 and not self.__is_count_select:
            raise ValueError("At least one column must be specified.")
        
        sql = ["SELECT"]

        if self.__is_count_select:
            sql.append("COUNT(*)")
        else: sql.append(", ".join(self.__columns))

        if self.__table_name is not None:
            sql.append("FROM")
            sql.append(self.__table_name)

        return (" ".join(sql), ())
