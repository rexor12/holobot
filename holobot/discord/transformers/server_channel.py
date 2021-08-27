from discord.abc import GuildChannel
from holobot.discord.sdk.servers.models import ServerChannel

def remote_to_local(entity: GuildChannel) -> ServerChannel:
    return ServerChannel(
        id=str(entity.id),
        name=entity.name
    )
