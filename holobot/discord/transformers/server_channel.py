from hikari import GuildChannel as HikariGuildChannel
from holobot.discord.sdk.servers.models import ServerChannel

def to_model(dto: HikariGuildChannel) -> ServerChannel:
    return ServerChannel(
        id=str(dto.id),
        name=dto.name or "Unknown"
    )
