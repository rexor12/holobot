import contextlib

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.servers.managers import IUserManager
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import MenuType, OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import (
    ServerChatInteractionContext, ServerUserInteractionContext
)
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from .. import IConfigProvider
from ..enums import ModeratorPermission
from .interactables.decorators import moderation_command, moderation_menu_item
from .responses import UserKickedResponse as UserKickedInteractionResponse
from .responses.menu_item_responses import UserKickedResponse as UserKickedMenuItemResponse

@injectable(IWorkflow)
class KickUserWorkflow(WorkflowBase):
    def __init__(
        self,
        config_provider: IConfigProvider,
        i18n_provider: II18nProvider,
        messaging: IMessaging,
        user_manager: IUserManager
    ) -> None:
        super().__init__()
        self.__config_provider = config_provider
        self.__i18n_provider = i18n_provider
        self.__messaging = messaging
        self.__user_manager = user_manager

    @moderation_command(
        description="Kicks a user from the server. The user can rejoin with an invitation.",
        name="kick",
        group_name="moderation",
        options=(
            Option("user", "The user to kick.", OptionType.USER),
            Option("reason", "The reason of the punishment.")
        ),
        required_moderator_permissions=ModeratorPermission.KICK_USERS
    )
    async def kick_user_via_command(
        self,
        context: ServerChatInteractionContext,
        user: int,
        reason: str
    ) -> InteractionResponse:
        user_id = str(user)
        reason = reason.strip()
        reason_length_range = self.__config_provider.get_reason_length_range()
        if len(reason) not in reason_length_range:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.reason_out_of_range_error",
                        { "min": reason_length_range.lower_bound, "max": reason_length_range.upper_bound }
                    )
                )
            )

        try:
            await self.__user_manager.kick_user(context.server_id, user_id, reason)
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
                        "extensions.moderation.kick_user_workflow.cannot_kick_user_error",
                        { "user_id": user_id }
                    ),
                    suppress_user_mentions=True
                )
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.kick_user_workflow.user_kicked_dm",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name,
                        "reason": reason
                    }
                )
            )

        return UserKickedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.kick_user_workflow.user_kicked",
                    {
                        "user_id": user_id,
                        "reason": reason
                    }
                ),
                suppress_user_mentions=True
            )
        )

    @moderation_menu_item(
        title="Kick",
        menu_type=MenuType.USER,
        priority=4,
        required_moderator_permissions=ModeratorPermission.KICK_USERS
    )
    async def kick_user_via_menu_item(
        self,
        context: ServerUserInteractionContext
    ) -> InteractionResponse:
        try:
            await self.__user_manager.kick_user(context.server_id, context.target_user_id, "Issued via menu item")
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
                        "extensions.moderation.kick_user_workflow.cannot_kick_user_error",
                        { "user_id": context.target_user_id }
                    ),
                    suppress_user_mentions=True
                )
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                context.target_user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.kick_user_workflow.user_kicked_dm_no_reason",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name
                    }
                )
            )

        return UserKickedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.kick_user_workflow.user_kicked_no_reason",
                    { "user_id": context.target_user_id }
                ),
                suppress_user_mentions=True
            )
        )
