from .moderation_command_base import ModerationCommandBase
from .responses import UserUnmutedResponse
from ..constants import MUTED_ROLE_NAME
from ..enums import ModeratorPermission
from discord.errors import Forbidden
from discord.member import Member
from discord.utils import get
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class UnmuteUserCommand(ModerationCommandBase):
    def __init__(self) -> None:
        super().__init__("unmute")
        self.group_name = "moderation"
        self.description = "Removes the muting from a user."
        self.options = [
            create_option("user", "The mention of the user to mute.", SlashCommandOptionType.STRING, True)
        ]
        self.required_moderator_permissions = ModeratorPermission.MUTE_USERS
    
    async def execute(self, context: SlashContext, user: str) -> CommandResponse:
        if (user_id := get_user_id(user)) is None:
            await reply(context, "You must mention a user correctly.")
            return CommandResponse()
        if context.guild is None:
            await reply(context, "You may use this command in a server only.")
            return CommandResponse()

        member = context.guild.get_member(int(user_id))
        if member is None:
            await reply(context, "The user you mentioned cannot be found.")
            return CommandResponse()
        if not isinstance(member, Member):
            await reply(context, "I'm sorry, but something went wrong internally. Please, try again later or contact your server administrator.")
            return CommandResponse()
        
        muted_role = get(context.guild.roles, name=MUTED_ROLE_NAME)
        if muted_role is None:
            await reply(context, "I cannot find a 'Muted' role, hence I cannot unmute the user. Have they been muted by a different bot?")
            return CommandResponse()
        
        try:
            await member.remove_roles(muted_role)
        except Forbidden:
            await reply(context, (
                "I cannot remove the 'Muted' role.\n"
                "Have you given me user management permissions?\n"
                "Do they have a higher ranking role?"
            ))
            return CommandResponse()

        await reply(context, f"{member.mention} has been unmuted.")
        return UserUnmutedResponse(
            author_id=str(context.author_id),
            user_id=user_id
        )
