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
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class UnmuteUserWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        messaging: IMessaging,
        mute_manager: IMuteManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__messaging = messaging
        self.__mute_manager = mute_manager

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
                action=ReplyAction(content=self.__i18n_provider.get("user_not_found_error"))
            )

        try:
            await self.__mute_manager.unmute_user(context.server_id, user_id)
        except UserNotFoundError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("user_not_found_error"))
            )
        except ForbiddenError:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.unmute_user_workflow.cannot_unmute_user_error",
                        { "user_id": user_id }
                    ),
                    suppress_user_mentions=True
                )
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.unmute_user_workflow.user_unmuted_dm",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name
                    }
                )
            )

        return UserUnmutedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.unmute_user_workflow.user_unmuted",
                    { "user_id": user_id }
                ),
                suppress_user_mentions=True
            )
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
                    content=self.__i18n_provider.get("user_not_found_error")
                )
            )
        except ForbiddenError:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.unmute_user_workflow.cannot_unmute_user_error",
                        { "user_id": context.target_user_id }
                    )
                )
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                context.target_user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.unmute_user_workflow.user_unmuted_dm",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name
                    }
                )
            )

        return UserUnmutedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.unmute_user_workflow.user_unmuted",
                    { "user_id": context.target_user_id }
                ),
                suppress_user_mentions=True
            )
        )
