from collections.abc import Awaitable, Callable

from asyncpg.connection import Connection

class MigrationPlan:
    @property
    def new_version(self) -> int:
        return self.__new_version

    def __init__(
        self,
        new_version: int,
        function: Callable[[Connection], Awaitable[None]]
    ):
        self.__new_version = new_version
        self.__function = function

    async def execute(self, connection: Connection):
        await self.__function(connection)
