from typing import Any, Tuple

from .compiled_pagination_query import CompiledPaginationQuery
from .iquery_part_builder import IQueryPartBuilder

class PaginateBuilder(IQueryPartBuilder):
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
        return CompiledPaginationQuery(
            *self.build(),
            self.__page_index,
            self.__page_size
        )

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        parent_sql = self.__parent_builder.build()
        arguments = [
            *parent_sql[1],
            self.__ordering_column,
            self.__page_index * self.__page_size,
            self.__page_size
        ]
        base_index = len(parent_sql[1])
        sql = [
            "WITH Data_CTE AS (",
            f"{parent_sql[0]}",
            "),",
            "Count_CTE AS (SELECT COUNT(*) AS _totalrows FROM Data_CTE)",
            f"SELECT * FROM Data_CTE CROSS JOIN Count_CTE ORDER BY ${base_index + 1}",
            f"OFFSET ${base_index + 2} ROWS FETCH NEXT ${base_index + 3} ROWS ONLY"
        ]

        return (" ".join(sql), tuple(arguments))
