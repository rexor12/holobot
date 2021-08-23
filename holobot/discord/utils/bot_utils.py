from ..bot import BotAccessor
from discord.guild import Guild, Member
from holobot.discord.sdk.exceptions import ServerNotFoundError, UserNotFoundError
from typing import Optional
    
def get_guild(self, server_id: str) -> Guild:
    guild: Optional[Guild] = BotAccessor.get_bot().get_guild(int(server_id))
    if not guild:
        raise ServerNotFoundError(server_id)
    
    return guild

def get_guild_member(server_id: str, user_id: str) -> Member:
    guild: Optional[Guild] = BotAccessor.get_bot().get_guild(int(server_id))
    if not guild:
        raise ServerNotFoundError(server_id)

    member = guild.get_member(int(user_id))
    if not member or not isinstance(member, Member):
        raise UserNotFoundError(user_id)
    
    return member
