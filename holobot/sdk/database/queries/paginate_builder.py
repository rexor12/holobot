from typing import Any

from holobot.sdk.exceptions import ArgumentError
from .compiled_pagination_query import CompiledPaginationQuery
from .enums import Order
from .icompileable_query_part_builder import ICompileableQueryPartBuilder
from .iquery_part_builder import IQueryPartBuilder

class PaginateBuilder(ICompileableQueryPartBuilder[CompiledPaginationQuery]):
    def __init__(
        self,
        parent_builder: IQueryPartBuilder,
        ordering_columns: tuple[tuple[str, Order], ...],
        page_index: int,
        page_size: int
    ) -> None:
        super().__init__()
        self.__parent_builder = parent_builder
        self.__ordering_columns = ordering_columns
        self.__page_index = page_index
        self.__page_size = page_size
        if len(ordering_columns) < 1:
            raise ArgumentError(
                "ordering_columns",
                "At least one ordering column must be specified."
            )

    def compile(self) -> CompiledPaginationQuery:
        return CompiledPaginationQuery(*self.build(), self.__page_index, self.__page_size)

    def build(self) -> tuple[str, tuple[Any, ...]]:
        parent_sql, parent_args = self.__parent_builder.build()
        ordering_columns = tuple(map(lambda i: i[0], self.__ordering_columns))
        arguments = (
            *parent_args,
            self.__page_index * self.__page_size,
            self.__page_size
        )
        base_index = len(parent_args) + 1
        sql = [
            f"WITH Data_CTE AS ({parent_sql}), ",
            "Count_CTE AS (SELECT COUNT(*) AS _totalrows FROM Data_CTE) ",
            "SELECT * FROM Data_CTE CROSS JOIN Count_CTE ORDER BY "
        ]
        for index in range(len(ordering_columns)):
            order = "ASC" if self.__ordering_columns[index][1] == Order.ASCENDING else "DESC"
            sql.append(f"{self.__ordering_columns[index][0]} {order}")
            if index < len(ordering_columns) - 1:
                sql.append(", ")

        sql.append(f" OFFSET ${base_index} ROWS FETCH NEXT ${base_index + 1} ROWS ONLY")

        return ("".join(sql), arguments)
