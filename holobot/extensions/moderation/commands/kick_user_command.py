from .moderation_command_base import ModerationCommandBase
from .responses import UserKickedResponse
from .. import IConfigProvider
from ..enums import ModeratorPermission
from holobot.discord.sdk import IMessaging, IUserManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class KickUserCommand(ModerationCommandBase):
    def __init__(self, config_provider: IConfigProvider, messaging: IMessaging, user_manager: IUserManager) -> None:
        super().__init__("kick")
        self.group_name = "moderation"
        self.description = "Kicks a user from the server. The user can rejoin with an invitation."
        self.options = [
            Option("user", "The mention of the user to kick."),
            Option("reason", "The reason of the punishment.")
        ]
        self.required_moderator_permissions = ModeratorPermission.MUTE_USERS
        self.__config_provider: IConfigProvider = config_provider
        self.__messaging: IMessaging = messaging
        self.__user_manager: IUserManager = user_manager
    
    async def execute(self, context: ServerChatInteractionContext, user: str, reason: str) -> CommandResponse:
        user = user.strip()
        reason = reason.strip()
        if (user_id := get_user_id(user)) is None:
            return CommandResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )

        reason_length_range = self.__config_provider.get_reason_length_range()
        if not len(reason) in reason_length_range:
            return CommandResponse(
                action=ReplyAction(content=f"The reason parameter's length must be between {reason_length_range.lower_bound} and {reason_length_range.upper_bound}.")
            )

        try:
            await self.__user_manager.kick_user(context.server_id, user_id, reason)
        except UserNotFoundError:
            return CommandResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )
        except ForbiddenError:
            return CommandResponse(
                action=ReplyAction(content=(
                    "I cannot kick the user.\n"
                    "Have you given me user management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        try:
            await self.__messaging.send_private_message(user_id, f"You have been kicked from {context.server_id} by {context.author_id} with the reason '{reason}'. I'm sorry this happened to you.")
        except ForbiddenError:
            pass

        return UserKickedResponse(
            author_id=str(context.author_id),
            user_id=user_id,
            reason=reason,
            action=ReplyAction(content=f"<@{user_id}> has been kicked. Reason: {reason}")
        )
