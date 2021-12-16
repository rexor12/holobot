from .moderation_command_base import ModerationCommandBase
from .responses import UserMutedResponse
from ..enums import ModeratorPermission
from ..managers import IMuteManager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.chrono import parse_interval
from typing import Optional

@injectable(CommandInterface)
class MuteUserCommand(ModerationCommandBase):
    def __init__(self, messaging: IMessaging, mute_manager: IMuteManager) -> None:
        super().__init__("mute")
        self.group_name = "moderation"
        self.description = "Mutes a user."
        self.options = [
            Option("user", "The mention of the user to mute."),
            Option("reason", "The reason of the punishment."),
            Option("duration", "The duration after which to lift the mute. Eg. 1h or 30m.", is_mandatory=False)
        ]
        self.required_moderator_permissions = ModeratorPermission.MUTE_USERS
        self.__messaging: IMessaging = messaging
        self.__mute_manager: IMuteManager = mute_manager
    
    async def execute(self, context: ServerChatInteractionContext, user: str, reason: str, duration: Optional[str] = None) -> CommandResponse:
        user = user.strip()
        reason = reason.strip()
        mute_duration = parse_interval(duration.strip()) if duration is not None else None
        if (user_id := get_user_id(user)) is None:
            return CommandResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )

        try:
            await self.__mute_manager.mute_user(context.server_id, user_id, reason, mute_duration)
        except ArgumentOutOfRangeError as error:
            if error.argument_name == "reason":
                return CommandResponse(
                    action=ReplyAction(content=f"The reason parameter's length must be between {error.lower_bound} and {error.upper_bound}.")
                )
            return CommandResponse(
                action=ReplyAction(content=f"The duration parameter's value must be between {error.lower_bound} and {error.upper_bound}.")
            )
        except UserNotFoundError:
            return CommandResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )
        except ForbiddenError:
            return CommandResponse(
                action=ReplyAction(content=(
                    "I cannot assign/create a 'Muted' role.\n"
                    "Have you given me role management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        try:
            await self.__messaging.send_private_message(user_id, f"You have been muted in {context.server_name} by {context.author_name} with the reason '{reason}'. I'm sorry this happened to you.")
        except ForbiddenError:
            pass

        return UserMutedResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            duration=mute_duration,
            action=ReplyAction(content=f"<@{user_id}> has been muted. Reason: {reason}")
        )
