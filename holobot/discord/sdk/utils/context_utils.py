from discord.embeds import Embed
from discord.ext.commands import Context
from discord.ext.commands.converter import PartialEmojiConverter
from discord.ext.commands.errors import PartialEmojiConversionFailure
from discord.guild import Guild
from discord.message import Message
from discord.partial_emoji import PartialEmoji
from discord.user import User
from discord_slash.context import SlashContext
from discord_slash.model import SlashMessage
from typing import Callable, Optional, Union

import re

mention_regex = re.compile(r"^<@!?(?P<id>\d+)>$")

emoji_converter = PartialEmojiConverter()

def find_member(context: Union[Context, SlashContext], name_or_mention: str) -> Optional[User]:
    guild = context.guild
    # An attempt to fix type hints for the messy discord.py.
    if not guild or not isinstance(guild, Guild):
        return None
    
    predicate: Callable[[User], bool] = lambda user: name_or_mention in user.display_name or name_or_mention in user.name
    if (match := mention_regex.match(name_or_mention)) is not None:
        predicate = lambda user: str(user.id) == match.group("id")
    for member in guild.members:
        # An attempt to fix type hints for the messy discord.py.
        member: User
        if predicate(member):
            return member
    return None

async def find_emoji(context: Union[Context, SlashContext], mention: str) -> Optional[PartialEmoji]:
    try:
        return await emoji_converter.convert(context, mention)
    except PartialEmojiConversionFailure:
        return None

def get_author_id(context: Union[Context, SlashContext]) -> str:
    if isinstance(context, SlashContext):
        return str(context.author.id)
    else: return str(context.author.id)

async def reply(context: Union[Context, SlashContext], content: Union[str, Embed]) -> Union[Message, SlashMessage]:
    if isinstance(context, SlashContext):
        if isinstance(content, str):
            return await context.send(content)
        else: return await context.send(embed=content)
    else:
        if isinstance(content, str):
            return await context.reply(content)
        else: return await context.reply(embed=content)
