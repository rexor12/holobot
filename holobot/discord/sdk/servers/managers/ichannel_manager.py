from ..models import ServerChannel
from holobot.discord.sdk.enums import Permission
from typing import Iterable

class IChannelManager:
    def get_channels(self, server_id: str) -> Iterable[ServerChannel]:
        raise NotImplementedError

    async def set_role_permissions(self, server_id: str, channel_id: str, role_id: str, *permissions: tuple[Permission, bool | None]) -> None:
        raise NotImplementedError
