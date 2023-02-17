from collections.abc import Awaitable
from typing import Any, Protocol

from asyncpg.connection import Connection

from holobot.sdk.database.statuses import CommandComplete

class ICompiledQuery(Protocol):
    def execute(self, connection: Connection) -> Awaitable[CommandComplete[Any]]:
        ...

    def fetch(self, connection: Connection) -> Awaitable[tuple[dict[str, Any], ...]]:
        ...

    def fetchrow(self, connection: Connection) -> Awaitable[dict[str, Any] | None]:
        ...

    def fetchval(self, connection: Connection) -> Awaitable[Any | None]:
        ...
