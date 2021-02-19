from asyncpg.connection import Connection
from typing import Callable, Coroutine

class MigrationPlan:
    def __init__(self, old_version: int, new_version: int,
        function: Callable[[Connection], Coroutine[None, None, None]]):
        self.old_version = old_version
        self.new_version = new_version
        self.__function = function
    
    async def execute(self, connection: Connection):
        await self.__function(connection)