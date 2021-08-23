from discord.ext.commands import Context
from discord.ext.commands.converter import EmojiConverter, PartialEmojiConverter
from discord.ext.commands.errors import EmojiNotFound, PartialEmojiConversionFailure
from discord.partial_emoji import PartialEmoji
from discord_slash.context import SlashContext
from typing import Optional, Union

partial_emoji_converter = PartialEmojiConverter()
emoji_converter = EmojiConverter()

async def find_emoji(context: Union[Context, SlashContext], name_or_mention: str) -> Optional[PartialEmoji]:
    name_or_mention = name_or_mention.strip()
    try:
        return await partial_emoji_converter.convert(context, name_or_mention)
    except PartialEmojiConversionFailure:
        pass
    
    try:
        return await emoji_converter.convert(context, name_or_mention)
    except EmojiNotFound:
        return None
