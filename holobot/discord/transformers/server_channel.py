from hikari import GuildChannel as HikariGuildChannel, GuildVoiceChannel

from holobot.discord.sdk.servers.models import ServerChannel

def to_model(dto: HikariGuildChannel) -> ServerChannel:
    return ServerChannel(
        id=dto.id,
        name=dto.name or "Unknown",
        is_voice=isinstance(dto, GuildVoiceChannel)
    )
