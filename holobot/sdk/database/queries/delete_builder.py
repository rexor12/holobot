from .iquery_part_builder import IQueryPartBuilder
from .where_builder import WhereBuilder
from typing import Any, Optional, Tuple

class DeleteBuilder(IQueryPartBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.__table_name: Optional[str] = None
    
    def from_table(self, table_name: str) -> 'DeleteBuilder':
        self.__table_name = table_name
        return self

    def where(self) -> WhereBuilder:
        return WhereBuilder(self)

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        if not self.__table_name:
            raise ValueError("The source table must be specified.")

        return (f"DELETE FROM {self.__table_name}", ())
