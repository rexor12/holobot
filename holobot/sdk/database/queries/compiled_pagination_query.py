from typing import Any

from asyncpg.connection import Connection

from .models import PaginationResult

# TODO Query string tracing.
class CompiledPaginationQuery:
    def __init__(
        self,
        query: str,
        arguments: tuple[Any, ...],
        page_index: int,
        page_size: int
    ) -> None:
        self.__query: str = query
        self.__arguments: tuple[Any, ...] = arguments
        self.__page_index: int = page_index
        self.__page_size: int = page_size
        # print(f"Query: {query}\nArgs: {", ".join(map(lambda i: str(i), arguments))}")

    async def fetch(self, connection: Connection) -> PaginationResult:
        records: list[Any] = await connection.fetch(self.__query, *self.__arguments)
        total_count = records[0]["_totalrows"] if records else 0
        return PaginationResult(
            self.__page_index,
            self.__page_size,
            total_count,
            records or ()
        )
