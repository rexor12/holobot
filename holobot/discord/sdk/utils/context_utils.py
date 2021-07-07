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
from holobot.sdk.utils import first_or_default
from typing import List, Optional, Tuple, Union

import re

mention_regex = re.compile(r"^<@!?(?P<id>\d+)>$")

emoji_converter = PartialEmojiConverter()

def find_member(context: Union[Context, SlashContext], name_or_mention: str) -> Optional[User]:
    guild = context.guild
    # An attempt to fix type hints for the messy discord.py.
    if not guild or not isinstance(guild, Guild):
        return None
    
    if (match := mention_regex.match(name_or_mention)) is not None:
        captured_match = match
        return first_or_default(guild.members, lambda user: str(user.id) == captured_match.group("id"))
    
    relevant_members: List[Tuple[User, int]] = []
    for member in guild.members:
        # An attempt to fix type hints for the messy discord.py.
        member: User
        relevance = __match_user_with_relevance(name_or_mention, member)
        if relevance > 0:
            relevant_members.append((member, relevance))
    
    best_match = first_or_default(sorted(relevant_members, key=lambda p: p[1], reverse=True))
    return best_match[0] if best_match is not None else None

def find_member_by_id(context: Union[Context, SlashContext], user_id: str) -> Optional[User]:
    guild = context.guild
    # An attempt to fix type hints for the messy discord.py.
    if not guild or not isinstance(guild, Guild):
        return None
    
    return guild.get_member(int(user_id))

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

def __match_with_relevance(pattern: str, value: str) -> int:
    relevance = 0
    pattern_lower = pattern.lower()
    value_lower = value.lower()

    # Containment, different casing.
    if not pattern_lower in value_lower:
        return relevance
    relevance = relevance + 1

    # Full match, different casing.
    if pattern_lower == value_lower:
        relevance = relevance + 1
    
    # Containment, same casing.
    if not pattern in value:
        return relevance
    relevance = relevance + 1

    # Full match, same casing.
    if not pattern == value:
        return relevance
    
    return relevance + 1

def __match_user_with_relevance(pattern: str, user: User) -> int:
    # Display names are more relevant than real names.
    relevance = __match_with_relevance(pattern, user.display_name)
    if relevance > 0:
        return relevance + 1
    return __match_with_relevance(pattern, user.name)
