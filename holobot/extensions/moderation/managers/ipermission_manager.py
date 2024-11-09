from typing import Protocol

from holobot.extensions.moderation.enums import ModeratorPermission

class IPermissionManager(Protocol):
    async def add_permissions(
        self,
        server_id: int,
        user_id: int,
        permissions: ModeratorPermission
    ) -> None:
        ...

    async def remove_permissions(
        self,
        server_id: int,
        user_id: int,
        permissions: ModeratorPermission
    ) -> None:
        ...

    async def remove_all_permissions(
        self,
        server_id: int,
        user_id: int
    ) -> bool:
        ...

    async def has_permissions(
        self,
        server_id: int,
        user_id: int,
        permissions: ModeratorPermission
    ) -> bool:
        ...
