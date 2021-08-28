from ..contexts import IContextManager
from ..transformers.emoji import remote_to_local
from discord.ext.commands.converter import EmojiConverter, PartialEmojiConverter
from discord.ext.commands.errors import EmojiNotFound, PartialEmojiConversionFailure
from discord.partial_emoji import PartialEmoji
from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.discord.sdk.models import Emoji, InteractionContext
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

partial_emoji_converter = PartialEmojiConverter()
emoji_converter = EmojiConverter()

@injectable(IEmojiDataProvider)
class EmojiDataProvider(IEmojiDataProvider):
    def __init__(self, context_manager: IContextManager) -> None:
        super().__init__()
        self.__context_manager: IContextManager = context_manager

    async def find_emoji(self, context: InteractionContext, name_or_mention: str) -> Optional[Emoji]:
        if not (emoji := await self.__find_emoji(context, name_or_mention)):
            return None
        return remote_to_local(emoji)

    async def __find_emoji(self, context: InteractionContext, name_or_mention: str) -> Optional[PartialEmoji]:
        tracked_context = await self.__context_manager.get_context(context.request_id)
        try:
            return await partial_emoji_converter.convert(tracked_context.context, name_or_mention)
        except PartialEmojiConversionFailure:
            pass
        
        try:
            return await emoji_converter.convert(tracked_context.context, name_or_mention)
        except EmojiNotFound:
            return None
