from discord.ext.commands import Context
from discord.guild import Guild
from discord.user import User
from discord_slash import SlashContext
from typing import Optional, Union

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

def get_author_id(context: Union[Context, SlashContext]) -> str:
    if isinstance(context, SlashContext):
        return str(context.author.id)
    else: return str(context.author.id)

async def reply(context: Union[Context, SlashContext], message: str) -> None:
    if isinstance(context, SlashContext):
        await context.send(message)
    else: await context.reply(message)
