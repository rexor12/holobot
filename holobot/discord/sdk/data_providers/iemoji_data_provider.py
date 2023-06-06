from collections.abc import Awaitable
from typing import Protocol

from holobot.discord.sdk.models import Emoji

class IEmojiDataProvider(Protocol):
    def find_emoji(
        self,
        name_or_mention: str,
        source_server_id: str | None = None
    ) -> Awaitable[Emoji | None]:
        ...

    def extract_id(self, mention: str) -> str:
        ...
