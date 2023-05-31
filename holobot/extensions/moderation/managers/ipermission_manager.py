from typing import Protocol

from holobot.extensions.moderation.enums import ModeratorPermission

class IPermissionManager(Protocol):
    async def add_permissions(
        self,
        server_id: str,
        user_id: str,
        permissions: ModeratorPermission
    ) -> None:
        ...

    async def remove_permissions(
        self,
        server_id: str,
        user_id: str,
        permissions: ModeratorPermission
    ) -> None:
        ...

    async def remove_all_permissions(
        self,
        server_id: str,
        user_id: str
    ) -> bool:
        ...

    async def has_permissions(
        self,
        server_id: str,
        user_id: str,
        permissions: ModeratorPermission
    ) -> bool:
        ...
