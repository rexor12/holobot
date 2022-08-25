from typing import Any, Protocol

from asyncpg.connection import Connection

from holobot.sdk.database.statuses import CommandComplete

class ICompiledQuery(Protocol):
    async def execute(self, connection: Connection) -> CommandComplete[Any]:
        ...

    async def fetch(self, connection: Connection) -> tuple[dict[str, Any], ...]:
        ...

    async def fetchrow(self, connection: Connection) -> dict[str, Any] | None:
        ...

    async def fetchval(self, connection: Connection) -> Any | None:
        ...
