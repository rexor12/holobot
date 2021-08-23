from .moderation_command_base import ModerationCommandBase
from .responses import UserBannedResponse
from .. import IConfigProvider
from ..enums import ModeratorPermission
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk import IMessaging, IUserManager
from holobot.discord.sdk.commands import CommandInterface, CommandResponse
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import get_user_id, reply
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class BanUserCommand(ModerationCommandBase):
    def __init__(self, config_provider: IConfigProvider, messaging: IMessaging, user_manager: IUserManager) -> None:
        super().__init__("ban")
        self.group_name = "moderation"
        self.description = "Bans a user from the server. The user cannot rejoin until the ban is lifted."
        self.options = [
            create_option("user", "The mention of the user to ban.", SlashCommandOptionType.STRING, True),
            create_option("reason", "The reason of the punishment.", SlashCommandOptionType.STRING, True),
            create_option("days", "If specified, the previous N days' messages are also removed.", SlashCommandOptionType.INTEGER, False)
        ]
        self.required_moderator_permissions = ModeratorPermission.BAN_USERS
        self.__config_provider: IConfigProvider = config_provider
        self.__messaging: IMessaging = messaging
        self.__user_manager: IUserManager = user_manager
    
    async def execute(self, context: SlashContext, user: str, reason: str, days: Optional[int] = None) -> CommandResponse:
        user = user.strip()
        reason = reason.strip()
        if (user_id := get_user_id(user)) is None:
            await reply(context, "You must mention a user correctly.")
            return CommandResponse()
        if context.guild is None:
            await reply(context, "You may use this command in a server only.")
            return CommandResponse()
        days = days if days is not None else 0
        if days < 0 or days > 7:
            await reply(context, "The days parameter's value must be between 0 and 7. If omitted, no messages are deleted.")
            return CommandResponse()
        reason_length_range = self.__config_provider.get_reason_length_range()
        if not len(reason) in reason_length_range:
            await reply(context, f"The reason parameter's length must be between {reason_length_range.lower_bound} and {reason_length_range.upper_bound}.")
            return CommandResponse()

        try:
            await self.__user_manager.ban_user(str(context.guild_id), user_id, reason, days)
        except UserNotFoundError:
            await reply(context, "The user you mentioned cannot be found.")
            return CommandResponse()
        except ForbiddenError:
            await reply(context, (
                "I cannot ban the user.\n"
                "Have you given me user management permissions?\n"
                "Do they have a role ranking higher than mine?"
            ))
            return CommandResponse()

        try:
            await self.__messaging.send_private_message(user_id, f"You have been banned from {context.guild.name} by {context.author.name} with the reason '{reason}'. I'm sorry this happened to you.")
        except ForbiddenError:
            pass

        await reply(context, f"<@{user_id}> has been banned. Reason: {reason}")
        return UserBannedResponse(
            author_id=str(context.author_id),
            user_id=user_id,
            reason=reason
        )
