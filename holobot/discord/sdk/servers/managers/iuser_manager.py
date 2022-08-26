from datetime import timedelta
from typing import Protocol

class IUserManager(Protocol):
    async def silence_user(
        self,
        server_id: str,
        user_id: str,
        duration: timedelta | None = None
    ) -> None:
        ...

    async def kick_user(self, server_id: str, user_id: str, reason: str) -> None:
        ...

    async def ban_user(
        self,
        server_id: str,
        user_id: str,
        reason: str,
        delete_message_days: int = 0
    ) -> None:
        ...

    async def assign_role(self, server_id: str, user_id: str, role_id: str) -> None:
        ...

    async def remove_role(self, server_id: str, user_id: str, role_id: str) -> None:
        ...

    async def unsilence_user(
        self,
        server_id: str,
        user_id: str
    ) -> None:
        ...
