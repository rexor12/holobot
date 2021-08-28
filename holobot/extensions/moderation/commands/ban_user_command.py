from .moderation_command_base import ModerationCommandBase
from .responses import UserBannedResponse
from .. import IConfigProvider
from ..enums import ModeratorPermission
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.servers.managers import IUserManager
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class BanUserCommand(ModerationCommandBase):
    def __init__(self, config_provider: IConfigProvider, messaging: IMessaging, user_manager: IUserManager) -> None:
        super().__init__("ban")
        self.group_name = "moderation"
        self.description = "Bans a user from the server. The user cannot rejoin until the ban is lifted."
        self.options = [
            Option("user", "The mention of the user to ban."),
            Option("reason", "The reason of the punishment."),
            Option("days", "If specified, the previous N days' messages are also removed.", OptionType.INTEGER, False)
        ]
        self.required_moderator_permissions = ModeratorPermission.BAN_USERS
        self.__config_provider: IConfigProvider = config_provider
        self.__messaging: IMessaging = messaging
        self.__user_manager: IUserManager = user_manager
    
    async def execute(self, context: ServerChatInteractionContext, user: str, reason: str, days: Optional[int] = None) -> CommandResponse:
        user = user.strip()
        reason = reason.strip()
        if (user_id := get_user_id(user)) is None:
            return CommandResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )
        days = days if days is not None else 0
        if days < 0 or days > 7:
            return CommandResponse(
                action=ReplyAction(content="The days parameter's value must be between 0 and 7. If omitted, no messages are deleted.")
            )
        reason_length_range = self.__config_provider.get_reason_length_range()
        if not len(reason) in reason_length_range:
            return CommandResponse(
                action=ReplyAction(content=f"The reason parameter's length must be between {reason_length_range.lower_bound} and {reason_length_range.upper_bound}.")
            )

        try:
            await self.__user_manager.ban_user(context.server_id, user_id, reason, days)
        except UserNotFoundError:
            return CommandResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )
        except ForbiddenError:
            return CommandResponse(
                action=ReplyAction(content=(
                    "I cannot ban the user.\n"
                    "Have you given me user management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        try:
            await self.__messaging.send_private_message(user_id, f"You have been banned from {context.server_id} by {context.author_id} with the reason '{reason}'. I'm sorry this happened to you.")
        except ForbiddenError:
            pass

        return UserBannedResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            action=ReplyAction(content=f"<@{user_id}> has been banned. Reason: {reason}")
        )
