from discord.ext.commands import Context
from discord.guild import Guild
from discord.user import User
from typing import Optional

def find_member(context: Context, name: str) -> Optional[User]:
    guild: Optional[Guild] = context.guild
    if guild is None:
        return None

    for user in guild.members:
        # NOTE: Member should be used here as the type, but discord.py is a mess,
        # because it somehow hides the "name" field. Since Member inherits from User,
        # using that here should be safe, too.
        user: User
        if name in user.display_name or name in user.name:
            return user
    return None
