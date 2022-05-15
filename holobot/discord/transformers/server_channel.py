from discord.abc import GuildChannel
from holobot.discord.sdk.servers.models import ServerChannel

def remote_to_local(entity: GuildChannel, server_id: str) -> ServerChannel:
    return ServerChannel(
        id=str(entity.id), # type: ignore
        server_id=server_id,
        name=entity.name # type: ignore
    )
