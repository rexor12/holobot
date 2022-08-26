from typing import Any

from asyncpg.connection import Connection

from holobot.sdk.database.statuses import CommandComplete
from .icompiled_query import ICompiledQuery

# TODO Query string tracing.
class CompiledQuery(ICompiledQuery):
    def __init__(self, query: str, arguments: tuple[Any, ...]) -> None:
        self.__query: str = query
        self.__arguments: tuple[Any, ...] = arguments

    async def execute(self, connection: Connection) -> CommandComplete[Any]:
        status = await connection.execute(self.__query, *self.__arguments)
        return CommandComplete.parse(status)

    async def fetch(self, connection: Connection) -> tuple[dict[str, Any], ...]:
        records: list[dict[str, Any]] = await connection.fetch(self.__query, *self.__arguments)
        return tuple(records)

    async def fetchrow(self, connection: Connection) -> dict[str, Any] | None:
        record: dict[str, Any] | None = await connection.fetchrow(self.__query, *self.__arguments)
        return record

    async def fetchval(self, connection: Connection) -> Any | None:
        return await connection.fetchval(self.__query, *self.__arguments)
