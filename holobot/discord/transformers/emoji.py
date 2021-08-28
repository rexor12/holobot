from discord.partial_emoji import PartialEmoji
from holobot.discord.sdk.models import Emoji

def remote_to_local(discord_emoji: PartialEmoji) -> Emoji:
    return Emoji(
        id=str(discord_emoji.id),
        url=discord_emoji.url.__str__()
    )
