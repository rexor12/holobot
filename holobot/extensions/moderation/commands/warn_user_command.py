from .moderation_command_base import ModerationCommandBase
from .responses import UserWarnedResponse
from .. import IConfigProvider
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class WarnUserCommand(ModerationCommandBase):
    def __init__(self, config_provider: IConfigProvider, member_data_provider: IMemberDataProvider, messaging: IMessaging, warn_manager: IWarnManager) -> None:
        super().__init__("warn")
        self.group_name = "moderation"
        self.description = "Warns a user, giving them one warn strike."
        self.options = [
            Option("user", "The mention of the user to warn."),
            Option("reason", "The reason of the punishment.")
        ]
        self.required_moderator_permissions = ModeratorPermission.WARN_USERS
        self.__config_provider: IConfigProvider = config_provider
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__messaging: IMessaging = messaging
        self.__warn_manager: IWarnManager = warn_manager

    async def execute(self, context: ServerChatInteractionContext, user: str, reason: str) -> CommandResponse:
        user = user.strip()
        reason = reason.strip()
        if (user_id := get_user_id(user)) is None:
            return CommandResponse(
                action=ReplyAction(
                    content="You must mention a user correctly."
                )
            )

        reason_length_range = self.__config_provider.get_reason_length_range()
        if not len(reason) in reason_length_range:
            return CommandResponse(
                action=ReplyAction(
                    content=f"The reason parameter's length must be between {reason_length_range.lower_bound} and {reason_length_range.upper_bound}."
                )
            )

        if not self.__member_data_provider.is_member(context.server_id, user_id):
            return CommandResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )

        await self.__warn_manager.warn_user(context.server_id, user_id, reason, context.author_id)

        try:
            await self.__messaging.send_private_message(user_id, f"You have been warned in {context.server_id} by {context.author_id} with the reason '{reason}'. Maybe you should behave yourself.")
        except ForbiddenError:
            pass

        return UserWarnedResponse(
            author_id=str(context.author_id),
            user_id=user_id,
            reason=reason,
            action=ReplyAction(
                content=f"<@{user_id}> has been warned. Reason: {reason}"
            )
        )
