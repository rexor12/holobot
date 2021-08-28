from discord.role import Role as DiscordRole
from holobot.discord.sdk.models import Role

def remote_to_local(discord_role: DiscordRole) -> Role:
    return Role(
        id=str(discord_role.id),
        name=discord_role.name
    )
