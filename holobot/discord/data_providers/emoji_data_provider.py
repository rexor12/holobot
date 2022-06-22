from ..bot import BotAccessor
from ..transformers.emoji import to_model
from hikari import Emoji as HikariEmoji
from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.discord.sdk.models import Emoji
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

import re

EMOJI_REGEX = re.compile(r"^<(?:\:[aA])?\:(?:\w+)\:(?P<id>\d+)>$")

@injectable(IEmojiDataProvider)
class EmojiDataProvider(IEmojiDataProvider):
    async def find_emoji(self, name_or_mention: str) -> Optional[Emoji]:
        return to_model(emoji) if (emoji := await self.__find_emoji(name_or_mention)) else None

    async def __find_emoji(self, name_or_mention: str) -> Optional[HikariEmoji]:
        # TODO Doesn't find emojis from other servers.
        if (match := EMOJI_REGEX.match(name_or_mention)) is not None:
            return BotAccessor.get_bot().cache.get_emoji(int(match["id"]))

        name_or_mention = name_or_mention.lower()
        return next((
                emoji for emoji in BotAccessor.get_bot().cache.get_emojis_view().values()
                if emoji.name.lower() == name_or_mention
            ),
            None
        )
