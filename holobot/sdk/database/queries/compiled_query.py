from typing import Any

import asyncpg

from holobot.sdk.database.exceptions import SerializationError
from holobot.sdk.database.statuses import CommandComplete
from .icompiled_query import ICompiledQuery

# TODO Query string tracing.
class CompiledQuery(ICompiledQuery):
    def __init__(self, query: str, arguments: tuple[Any, ...]) -> None:
        self.__query: str = query
        self.__arguments: tuple[Any, ...] = arguments

    async def execute(self, connection: asyncpg.Connection) -> CommandComplete[Any]:
        try:
            status = await connection.execute(self.__query, *self.__arguments)

            return CommandComplete.parse(status)
        except asyncpg.exceptions.SerializationError as error:
            raise SerializationError(str(error)) from error

    async def fetch(self, connection: asyncpg.Connection) -> tuple[dict[str, Any], ...]:
        try:
            records: list[dict[str, Any]] = await connection.fetch(self.__query, *self.__arguments)

            return tuple(records)
        except asyncpg.exceptions.SerializationError as error:
            raise SerializationError(str(error)) from error

    async def fetchrow(self, connection: asyncpg.Connection) -> dict[str, Any] | None:
        try:
            record: dict[str, Any] | None = await connection.fetchrow(
                self.__query,
                *self.__arguments
            )

            return record
        except asyncpg.exceptions.SerializationError as error:
            raise SerializationError(str(error)) from error

    async def fetchval(self, connection: asyncpg.Connection) -> Any | None:
        try:
            return await connection.fetchval(self.__query, *self.__arguments)
        except asyncpg.exceptions.SerializationError as error:
            raise SerializationError(str(error)) from error
