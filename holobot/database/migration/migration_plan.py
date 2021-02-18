from asyncpg.connection import Connection

class MigrationPlan:
    def __init__(self, old_version: int, new_version: int, func):
        self.old_version = old_version
        self.new_version = new_version
        self.__func = func
    
    async def execute(self, connection: Connection):
        await self.__func(connection)