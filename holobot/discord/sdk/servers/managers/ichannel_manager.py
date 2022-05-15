from ..models import ServerChannel
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.servers.models import ServerAudioChannel
from typing import Iterable, Optional, Tuple, Union

class IChannelManager:
    def get_audio_channel(self, server_id: str, channel_id: str) -> Optional[ServerAudioChannel]:
        raise NotImplementedError

    def get_channels(self, server_id: str) -> Iterable[ServerChannel]:
        raise NotImplementedError

    async def set_role_permissions(self, server_id: str, channel_id: str, role_id: str, *permissions: Tuple[Permission, Union[bool, None]]) -> None:
        raise NotImplementedError
