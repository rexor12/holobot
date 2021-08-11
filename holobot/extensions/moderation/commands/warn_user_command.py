from .moderation_command_base import ModerationCommandBase
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from discord.member import Member
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class WarnUserCommand(ModerationCommandBase):
    def __init__(self, warn_manager: IWarnManager) -> None:
        super().__init__("warn")
        self.group_name = "moderation"
        self.description = "Warns a user, giving them one warn strike."
        self.options = [
            create_option("user", "The mention of the user to warn.", SlashCommandOptionType.STRING, True),
            create_option("reason", "The reason of the punishment.", SlashCommandOptionType.STRING, True)
        ]
        self.required_moderator_permissions = ModeratorPermission.WARN_USERS
        self.__warn_manager: IWarnManager = warn_manager
    
    async def execute(self, context: SlashContext, user: str, reason: str) -> None:
        # TODO Reason length validation + trim.
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
        
        await self.__warn_manager.warn_user(str(context.guild_id), user_id, reason, str(context.author_id))
        await reply(context, f"{member.mention} has been warned. Reason: {reason}")
