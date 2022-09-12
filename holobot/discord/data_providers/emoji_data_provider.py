import re

from hikari import Emoji as HikariEmoji, urls
from hikari.internal import routes

from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.discord.sdk.models import Emoji
from holobot.sdk.ioc.decorators import injectable
from ..bot import get_bot
from ..transformers.emoji import to_model

EMOJI_REGEX = re.compile(r"<(?P<flags>[^:]*):(?P<name>[^:]*):(?P<id>\d+)>")

@injectable(IEmojiDataProvider)
class EmojiDataProvider(IEmojiDataProvider):
    async def find_emoji(self, name_or_mention: str) -> Emoji | None:
        emoji = await self.__find_emoji(name_or_mention)
        if isinstance(emoji, Emoji):
            return emoji

        return to_model(emoji) if emoji else None

    async def __find_emoji(self, name_or_mention: str) -> HikariEmoji | Emoji | None:
        if (match := EMOJI_REGEX.match(name_or_mention)) is not None:
            if emoji := get_bot().cache.get_emoji(int(match["id"])):
                return emoji
            else:
                return EmojiDataProvider.__create_unknown_emoji(match, name_or_mention)

        name_or_mention = name_or_mention.lower()
        return next((
                emoji for emoji in get_bot().cache.get_emojis_view().values()
                if emoji.name.lower() == name_or_mention
            ),
            None
        )

    @staticmethod
    def __create_unknown_emoji(emoji_match: re.Match[str], mention: str) -> Emoji:
        is_animated = emoji_match["flags"] in ("a", "A")
        extension = "gif" if is_animated else "png"
        identifier = emoji_match["id"]
        return Emoji(
            identifier=None,
            url=routes.CDN_CUSTOM_EMOJI.compile(
                urls.CDN_URL,
                emoji_id=identifier,
                file_format=extension
            ),
            mention=mention,
            is_known=False
        )
