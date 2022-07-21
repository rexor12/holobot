from .join_builder import JoinBuilder, JOIN_TYPE
from .iquery_part_builder import IQueryPartBuilder
from .where_builder import WhereBuilder
from typing import Any, List, Optional, Tuple

class SelectBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.__columns: List[str] = []
        self.__table_name: Optional[str] = None
        self.__table_alias: Optional[str] = None
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
    
    def from_table(self, table_name: str, alias: Optional[str] = None) -> 'SelectBuilder':
        self.__table_name = table_name
        self.__table_alias = alias
        return self

    def join(
        self,
        table_name: str,
        left_column: str,
        right_column: str,
        alias: Optional[str] = None,
        join_type: JOIN_TYPE = "LEFT"
    ) -> JoinBuilder:
        return JoinBuilder(
            self,
            table_name,
            left_column,
            right_column,
            alias,
            join_type
        )

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if len(self.__columns) == 0 and not self.__is_count_select:
            raise ValueError("At least one column must be specified.")

        sql = ["SELECT"]

        if self.__is_count_select:
            sql.append("COUNT(*)")
        else: sql.append(", ".join(self.__columns))

        if self.__table_name:
            sql.append("FROM")
            sql.append(self.__table_name)
            if self.__table_alias:
                sql.append("AS ")
                sql.append(self.__table_alias)

        return (" ".join(sql), ())
