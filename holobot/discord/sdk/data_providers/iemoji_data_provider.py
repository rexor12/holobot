from typing import Protocol

from holobot.discord.sdk.models import Emoji

class IEmojiDataProvider(Protocol):
    async def find_emoji(self, name_or_mention: str) -> Emoji | None:
        ...
