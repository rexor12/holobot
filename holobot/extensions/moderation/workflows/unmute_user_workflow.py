import contextlib

from .interactables.decorators import moderation_command, moderation_menu_item
from .responses import UserUnmutedResponse as UserUnmutedInteractionResponse
from .responses.menu_item_responses import UserUnmutedResponse as UserUnmutedMenuItemResponse
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
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class UnmuteUserWorkflow(WorkflowBase):
    def __init__(
        self,
        messaging: IMessaging,
        mute_manager: IMuteManager
    ) -> None:
        super().__init__()
        self.__messaging: IMessaging = messaging
        self.__mute_manager: IMuteManager = mute_manager

    @moderation_command(
        description="Removes the muting from a user.",
        name="unmute",
        group_name="moderation",
        options=(
            Option("user", "The mention of the user to mute."),
        ),
        required_moderator_permissions=ModeratorPermission.MUTE_USERS
    )
    async def unmute_user_via_command(
        self,
        context: ServerChatInteractionContext,
        user: str
    ) -> InteractionResponse:
        user = user.strip()
        if (user_id := get_user_id(user)) is None:
            return InteractionResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )

        try:
            await self.__mute_manager.unmute_user(context.server_id, user_id)
        except UserNotFoundError:
            return InteractionResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )
        except ForbiddenError:
            return InteractionResponse(
                action=ReplyAction(content=(
                    "I cannot remove the 'Muted' role.\n"
                    "Have you given me role management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(user_id, f"You have been unmuted in {context.server_name} by {context.author_name}. Make sure you behave next time.")

        return UserUnmutedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            action=ReplyAction(content=f"<@{user_id}> has been unmuted.")
        )

    @moderation_menu_item(
        title="Unmute",
        menu_type=MenuType.USER,
        priority=3,
        required_moderator_permissions=ModeratorPermission.MUTE_USERS
    )
    async def unmute_user_via_menu_item(
        self,
        context: ServerUserInteractionContext
    ) -> InteractionResponse:
        try:
            await self.__mute_manager.unmute_user(context.server_id, context.target_user_id)
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
                    "I cannot remove the 'Muted' role.\n"
                    "Have you given me role management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(context.target_user_id, f"You have been unmuted in {context.server_name} by {context.author_name}. Make sure you behave next time.")

        return UserUnmutedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=f"<@{context.target_user_id}> has been unmuted."
            )
        )
