from .permission_utils import has_permissions
from ..enums import Permission
from discord.channel import TextChannel
from discord.embeds import Embed
from discord.ext.commands import Context
from discord.ext.commands.converter import EmojiConverter, PartialEmojiConverter
from discord.ext.commands.errors import EmojiNotFound, PartialEmojiConversionFailure
from discord.guild import Guild
from discord.member import Member
from discord.message import Message
from discord.partial_emoji import PartialEmoji
from discord.permissions import Permissions
from discord.user import User
from discord_slash.context import SlashContext
from discord_slash.model import SlashMessage
from holobot.sdk.utils import first_or_default
from typing import List, Optional, Tuple, Union

import re

mention_regex = re.compile(r"^<@!?(?P<id>\d+)>$")
channel_regex = re.compile(r"^<#(?P<id>\d+)>$")

partial_emoji_converter = PartialEmojiConverter()
emoji_converter = EmojiConverter()

def find_member(context: Union[Context, SlashContext], name_or_mention: str) -> Optional[User]:
    name_or_mention = name_or_mention.strip()
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
    user_id = user_id.strip()
    guild = context.guild
    # An attempt to fix type hints for the messy discord.py.
    if not guild or not isinstance(guild, Guild):
        return None
    
    return guild.get_member(int(user_id))

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

def get_author_id(context: Union[Context, SlashContext]) -> str:
    if isinstance(context, SlashContext):
        return str(context.author.id)
    else: return str(context.author.id)

def get_channel_id(context: Union[Context, SlashContext], mention: Optional[str] = None) -> str:
    if mention is None or (channel_match := channel_regex.match(mention)) is None:
        return str(context.channel.id)
    return channel_match.group("id")

def has_channel_permission(context: Union[Context, SlashContext], user: Union[User, Member], permissions: Permission) -> bool:
    channel = context.channel
    if channel is None or not isinstance(channel, TextChannel):
        return False
    user_permissions = channel.permissions_for(user)
    if not isinstance(user_permissions, Permissions):
        return False
    return has_permissions(user_permissions, permissions)

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
