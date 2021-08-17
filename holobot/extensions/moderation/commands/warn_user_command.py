from .moderation_command_base import ModerationCommandBase
from .responses import UserWarnedResponse
from .. import IConfigProvider
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from discord.member import Member
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class WarnUserCommand(ModerationCommandBase):
    def __init__(self, config_provider: IConfigProvider, messaging: IMessaging, warn_manager: IWarnManager) -> None:
        super().__init__("warn")
        self.group_name = "moderation"
        self.description = "Warns a user, giving them one warn strike."
        self.options = [
            create_option("user", "The mention of the user to warn.", SlashCommandOptionType.STRING, True),
            create_option("reason", "The reason of the punishment.", SlashCommandOptionType.STRING, True)
        ]
        self.required_moderator_permissions = ModeratorPermission.WARN_USERS
        self.__warn_manager: IWarnManager = warn_manager
        self.__messaging: IMessaging = messaging
        self.__config_provider: IConfigProvider = config_provider
    
    async def execute(self, context: SlashContext, user: str, reason: str) -> CommandResponse:
        user = user.strip()
        reason = reason.strip()
        if (user_id := get_user_id(user)) is None:
            await reply(context, "You must mention a user correctly.")
            return CommandResponse()
        if context.guild is None:
            await reply(context, "You may use this command in a server only.")
            return CommandResponse()
        reason_length_range = self.__config_provider.get_reason_length_range()
        if not len(reason) in reason_length_range:
            await reply(context, f"The reason parameter's length must be between {reason_length_range.lower_bound} and {reason_length_range.upper_bound}.")
            return CommandResponse()

        member = context.guild.get_member(int(user_id))
        if member is None:
            await reply(context, "The user you mentioned cannot be found.")
            return CommandResponse()
        if not isinstance(member, Member):
            await reply(context, "I'm sorry, but something went wrong internally. Please, try again later or contact your server administrator.")
            return CommandResponse()
        
        await self.__warn_manager.warn_user(str(context.guild_id), user_id, reason, str(context.author_id))
        await self.__messaging.send_dm(user_id, f"You have been warned in {context.guild.name} by {context.author.name} with the reason '{reason}'. Maybe you should behave yourself.")
        await reply(context, f"{member.mention} has been warned. Reason: {reason}")
        return UserWarnedResponse(
            author_id=str(context.author_id),
            user_id=user_id,
            reason=reason
        )
