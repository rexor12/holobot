from ..statuses import CommandComplete
from asyncpg.connection import Connection
from typing import Any, Dict, List, Optional, Tuple

# TODO Query string tracing.
class CompiledQuery:
    def __init__(self, query: str, arguments: Tuple[Any, ...]) -> None:
        self.__query: str = query
        self.__arguments: Tuple[Any, ...] = arguments
    
    async def execute(self, connection: Connection) -> CommandComplete[Any]:
        status = await connection.execute(self.__query, *self.__arguments)
        return CommandComplete.parse(status)
    
    async def fetch(self, connection: Connection) -> Tuple[Dict[str, Any], ...]:
        records: List[Dict[str, Any]] = await connection.fetch(self.__query, *self.__arguments)
        return tuple(records)
    
    async def fetchrow(self, connection: Connection) -> Optional[Dict[str, Any]]:
        record: Optional[Dict[str, Any]] = await connection.fetchrow(self.__query, *self.__arguments)
        return record
    
    async def fetchval(self, connection: Connection) -> Optional[Any]:
        return await connection.fetchval(self.__query, *self.__arguments)
