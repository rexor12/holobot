from .moderation_command_base import ModerationCommandBase
from .responses import UserUnmutedResponse
from ..enums import ModeratorPermission
from ..managers import IMuteManager
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class UnmuteUserCommand(ModerationCommandBase):
    def __init__(self, mute_manager: IMuteManager) -> None:
        super().__init__("unmute")
        self.group_name = "moderation"
        self.description = "Removes the muting from a user."
        self.options = [
            Option("user", "The mention of the user to mute.")
        ]
        self.required_moderator_permissions = ModeratorPermission.MUTE_USERS
        self.__mute_manager: IMuteManager = mute_manager
    
    async def execute(self, context: ServerChatInteractionContext, user: str) -> CommandResponse:
        user = user.strip()
        if (user_id := get_user_id(user)) is None:
            return CommandResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )

        try:
            await self.__mute_manager.unmute_user(context.server_id, user_id)
        except UserNotFoundError:
            return CommandResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )
        except ForbiddenError:
            return CommandResponse(
                action=ReplyAction(content=(
                    "I cannot remove the 'Muted' role.\n"
                    "Have you given me role management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        return UserUnmutedResponse(
            author_id=str(context.author_id),
            user_id=user_id,
            action=ReplyAction(content=f"<@{user_id}> has been unmuted.")
        )
