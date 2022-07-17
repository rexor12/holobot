from typing import Optional

import contextlib

from .interactables.decorators import moderation_command, moderation_menu_item
from .responses import UserMutedResponse as UserMutedInteractionResponse
from .responses.menu_item_responses import UserMutedResponse as UserMutedMenuItemResponse
from ..enums import ModeratorPermission
from ..managers import IMuteManager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import MenuType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext, ServerUserInteractionContext
from holobot.sdk.chrono import parse_interval
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(IWorkflow)
class MuteUserWorkflow(WorkflowBase):
    def __init__(
        self,
        log: LogInterface,
        messaging: IMessaging,
        mute_manager: IMuteManager
    ) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "MuteUserWorkflow")
        self.__messaging: IMessaging = messaging
        self.__mute_manager: IMuteManager = mute_manager

    @moderation_command(
        description="Mutes a user.",
        name="mute",
        group_name="moderation",
        options=(
            Option("user", "The mention of the user to mute."),
            Option("reason", "The reason of the punishment."),
            Option("duration", "The duration after which to lift the mute. Eg. 1h or 30m.", is_mandatory=False)
        ),
        required_moderator_permissions=ModeratorPermission.MUTE_USERS
    )
    async def mute_user_via_command(
        self,
        context: ServerChatInteractionContext,
        user: str,
        reason: str,
        duration: Optional[str] = None
    ) -> InteractionResponse:
        user = user.strip()
        reason = reason.strip()
        mute_duration = parse_interval(duration.strip()) if duration is not None else None
        if (user_id := get_user_id(user)) is None:
            return InteractionResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )

        try:
            await self.__mute_manager.mute_user(context.server_id, user_id, reason, mute_duration)
        except ArgumentOutOfRangeError as error:
            if error.argument_name == "reason":
                return InteractionResponse(
                    action=ReplyAction(content=f"The reason parameter's length must be between {error.lower_bound} and {error.upper_bound}.")
                )
            return InteractionResponse(
                action=ReplyAction(content=f"The duration parameter's value must be between {error.lower_bound} and {error.upper_bound}.")
            )
        except UserNotFoundError:
            return InteractionResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )
        except ForbiddenError as error:
            self.__log.error("Failed to mute user.", error)
            return InteractionResponse(
                action=ReplyAction(content=(
                    "I cannot assign/create a 'Muted' role.\n"
                    "Have you given me role management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(user_id, f"You have been muted in {context.server_name} by {context.author_name} with the reason '{reason}'. I'm sorry this happened to you.")

        return UserMutedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            duration=mute_duration,
            action=ReplyAction(content=f"<@{user_id}> has been muted. Reason: {reason}")
        )

    @moderation_menu_item(
        title="Mute",
        menu_type=MenuType.USER,
        priority=2,
        required_moderator_permissions=ModeratorPermission.MUTE_USERS
    )
    async def mute_user_via_menu_item(
        self,
        context: ServerUserInteractionContext
    ) -> InteractionResponse:
        try:
            await self.__mute_manager.mute_user(context.server_id, context.target_user_id, "Issued via menu item")
        except UserNotFoundError:
            return InteractionResponse(
                action=ReplyAction(
                    content="The specified user cannot be found."
                )
            )
        except ForbiddenError:
            return InteractionResponse(
                action=ReplyAction(
                    content=(
                    "I cannot assign/create a 'Muted' role.\n"
                    "Have you given me role management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(context.target_user_id, f"You have been muted in {context.server_name} by {context.author_name}. I'm sorry this happened to you.")

        return UserMutedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=f"<@{context.target_user_id}> has been muted."
            )
        )
