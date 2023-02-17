from collections.abc import Awaitable

import asyncpg

from holobot.sdk.database import ISession
from holobot.sdk.threading.utils import COMPLETED_TASK

class Session(ISession):
    def __init__(
        self,
        connection: asyncpg.Connection,
        pool: asyncpg.pool.Pool | None
    ) -> None:
        super().__init__()
        self.__connection = connection
        self.__pool = pool

    @property
    def connection(self) -> asyncpg.Connection:
        return self.__connection

    def _on_dispose(self) -> Awaitable[None]:
        if self.__pool:
            return self.__pool.release(self.__connection)

        return COMPLETED_TASK
