from typing import Any

from .compiled_pagination_query import CompiledPaginationQuery
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .iquery_part_builder import IQueryPartBuilder

class PaginateBuilder(ICompileableQueryPartBuilder[CompiledPaginationQuery]):
    def __init__(
        self,
        parent_builder: IQueryPartBuilder,
        ordering_column: str,
        page_index: int,
        page_size: int
    ) -> None:
        super().__init__()
        self.__parent_builder: IQueryPartBuilder = parent_builder
        self.__ordering_column: str = ordering_column
        self.__page_index: int = page_index
        self.__page_size: int = page_size

    def compile(self) -> CompiledPaginationQuery:
        return CompiledPaginationQuery(*self.build(), self.__page_index, self.__page_size)

    def build(self) -> tuple[str, tuple[Any, ...]]:
        parent_sql, parent_args = self.__parent_builder.build()
        arguments = (
            *parent_args,
            self.__ordering_column,
            self.__page_index * self.__page_size,
            self.__page_size
        )
        base_index = len(parent_args)
        sql = (
            f"WITH Data_CTE AS ({parent_sql}), "
            "Count_CTE AS (SELECT COUNT(*) AS _totalrows FROM Data_CTE) "
            f"SELECT * FROM Data_CTE CROSS JOIN Count_CTE ORDER BY ${base_index + 1} "
            f"OFFSET ${base_index + 2} ROWS FETCH NEXT ${base_index + 3} ROWS ONLY"
        )

        return (sql, arguments)
