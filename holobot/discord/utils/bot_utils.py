from hikari import Guild, GuildChannel, Member, Role, User

from holobot.discord.bot import BotAccessor
from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, RoleNotFoundError, ServerNotFoundError, UserNotFoundError
)
from holobot.sdk.utils import first_or_default, rank_match

def get_guild(server_id: str) -> Guild:
    guild: Guild | None = BotAccessor.get_bot().cache.get_available_guild(int(server_id))
    if not guild:
        raise ServerNotFoundError(server_id)

    return guild

def get_guild_channel(server_id: str, channel_id: str) -> GuildChannel:
    guild = get_guild(server_id)
    channel = guild.get_channel(int(channel_id))
    if not channel:
        raise ChannelNotFoundError(channel_id)

    return channel

def get_guild_member(server_id: str, user_id: str) -> Member:
    guild = get_guild(server_id)
    member = guild.get_member(int(user_id))
    if not member or not isinstance(member, Member):
        raise UserNotFoundError(user_id)

    return member

def get_guild_member_by_name(server_id: str, user_name: str) -> Member:
    guild = get_guild(server_id)
    relevant_members: list[tuple[Member, int]] = []
    for member in guild.get_members().values():
        relevance = __match_user_with_relevance(user_name, member)
        if relevance > 0:
            relevant_members.append((member, relevance))

    best_match = first_or_default(sorted(relevant_members, key=lambda p: p[1], reverse=True))
    if not best_match:
        raise UserNotFoundError(user_name)

    return best_match[0]

def get_guild_role(server_id: str, role_id: str) -> Role:
    guild = get_guild(server_id)
    role = guild.get_role(int(role_id))
    if not role:
        raise RoleNotFoundError(server_id, role_id)

    return role

def get_user(user_id: str) -> User:
    if not (user := BotAccessor.get_bot().cache.get_user(int(user_id))):
        raise UserNotFoundError(user_id)

    return user

def __match_user_with_relevance(pattern: str, user: Member) -> int:
    # Display names are more relevant than real names.
    relevance = rank_match(pattern, user.display_name)
    if relevance > 0:
        return relevance + 1

    return rank_match(pattern, user.username)
