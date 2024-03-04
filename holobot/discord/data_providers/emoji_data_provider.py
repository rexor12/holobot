import re

from hikari import Emoji as HikariEmoji, urls
from hikari.internal import routes

from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.discord.sdk.models import Emoji
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from ..bot import get_bot
from ..transformers.emoji import to_model

EMOJI_REGEX = re.compile(r"<(?P<flags>[^:]*):(?P<name>[^:]*):(?P<id>\d+)>")

@injectable(IEmojiDataProvider)
class EmojiDataProvider(IEmojiDataProvider):
    async def find_emoji(
        self,
        name_or_mention: str,
        source_server_id: str | None = None
    ) -> Emoji | None:
        emoji = await self.__find_emoji(name_or_mention, source_server_id)
        if isinstance(emoji, Emoji):
            return emoji

        return to_model(emoji) if emoji else None

    def extract_id(self, mention: str) -> str:
        if not (match := EMOJI_REGEX.match(mention)):
            raise ArgumentError("mention", "Invalid emoji mention.")

        return match.group("id")

    async def __find_emoji(
        self,
        name_or_mention: str,
        source_server_id: str | None = None
    ) -> HikariEmoji | Emoji | None:
        if (match := EMOJI_REGEX.match(name_or_mention)) is not None:
            if emoji := get_bot().cache.get_emoji(int(match["id"])):
                if not source_server_id or str(emoji.guild_id) == source_server_id:
                    return emoji
                return None

            return EmojiDataProvider.__create_unknown_emoji(match, name_or_mention)

        name_or_mention = name_or_mention.lower()
        return next((
                emoji for emoji in get_bot().cache.get_emojis_view().values()
                if (
                    (not source_server_id or str(emoji.guild_id) == source_server_id)
                    and emoji.name.lower() == name_or_mention
                )
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
            name=emoji_match["name"],
            url=routes.CDN_CUSTOM_EMOJI.compile(
                urls.CDN_URL,
                emoji_id=identifier,
                file_format=extension
            ),
            mention=mention,
            is_known=False,
            is_animated=is_animated
        )
