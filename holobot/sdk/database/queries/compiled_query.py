from .exceptions import QueryFailedError
from asyncpg.connection import Connection
from typing import Any, Dict, List, Optional, Tuple

# TODO Query string tracing.
class CompiledQuery:
    def __init__(self, query: str, arguments: Tuple[Any, ...]) -> None:
        self.__query: str = query
        self.__arguments: Tuple[Any, ...] = arguments
    
    async def execute(self, connection: Connection) -> None:
        await connection.execute(self.__query, *self.__arguments)
    
    async def fetch(self, connection: Connection) -> Tuple[Dict[str, Any], ...]:
        records: List[Dict[str, Any]] = await connection.fetch(self.__query, *self.__arguments)
        return tuple(records)
    
    async def fetchrow(self, connection: Connection) -> Dict[str, Any]:
        record: Optional[Dict[str, Any]] = await connection.fetchrow(self.__query, *self.__arguments)
        if record is None:
            raise QueryFailedError(self.__query, "asyncpg returned a None-value.")
        return record
    
    async def fetchval(self, connection: Connection) -> Optional[Any]:
        return await connection.fetchval(self.__query, *self.__arguments)
