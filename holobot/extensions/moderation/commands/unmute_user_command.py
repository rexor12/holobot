from discord.abc import GuildChannel
from .moderation_command_base import ModerationCommandBase
from ..enums import ModeratorPermission
from discord.errors import Forbidden
from discord.guild import Guild
from discord.member import Member
from discord.role import Role
from discord.utils import get
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.ioc.decorators import injectable
from typing import List, Optional

@injectable(CommandInterface)
class UnmuteUserCommand(ModerationCommandBase):
    def __init__(self) -> None:
        super().__init__("unmute")
        self.group_name = "moderation"
        self.description = "Removes the muting from a user."
        self.options = [
            create_option("user", "The mention of the user to mute.", SlashCommandOptionType.STRING, True)
        ]
        self.required_moderator_permissions = ModeratorPermission.MUTE
    
    async def execute(self, context: SlashContext, user: str) -> None:
        if (user_id := get_user_id(user)) is None:
            await reply(context, "You must mention a user correctly.")
            return
        if context.guild is None:
            await reply(context, "You may use this command in a server only.")
            return

        member = context.guild.get_member(int(user_id))
        if member is None:
            await reply(context, "The user you mentioned cannot be found.")
            return
        if not isinstance(member, Member):
            await reply(context, "I'm sorry, but something went wrong internally. Please, try again later or contact your server administrator.")
            return
        
        muted_role = get(context.guild.roles, name="Muted")
        if muted_role is None:
            await reply(context, "I cannot find a 'Muted' role, hence I cannot unmute the user. Have they been muted by a different bot?")
            return
        
        await member.remove_roles(muted_role)
        await reply(context, f"{member.mention} has been unmuted.")
