from typing import Protocol

import asyncpg

from holobot.sdk.concurrency import IAsyncDisposable

class ISession(IAsyncDisposable, Protocol):
    """Represents a database session."""

    @property
    def connection(self) -> asyncpg.Connection:
        """Gets the asyncpg connection that belongs to this session.

        :return: The session's connection.
        :rtype: asyncpg.Connection
        """
        ...
