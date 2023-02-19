import contextlib

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
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
from ..managers import IWarnManager
from .interactables.decorators import moderation_command, moderation_menu_item
from .responses import UserWarnedResponse as UserWarnedInteractionResponse
from .responses.menu_item_responses import UserWarnedResponse as UserWarnedMenuItemResponse

@injectable(IWorkflow)
class WarnUserWorkflow(WorkflowBase):
    def __init__(
        self,
        config_provider: IConfigProvider,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        messaging: IMessaging,
        warn_manager: IWarnManager
    ) -> None:
        super().__init__()
        self.__config_provider = config_provider
        self.__i18n_provider = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__messaging = messaging
        self.__warn_manager = warn_manager

    @moderation_command(
        description="Warns a user, giving them one warn strike.",
        name="warn",
        group_name="moderation",
        options=(
            Option("user", "The user to warn.", type=OptionType.USER),
            Option("reason", "The reason of the punishment.")
        ),
        required_moderator_permissions=ModeratorPermission.WARN_USERS
    )
    async def warn_user_via_command(
        self,
        context: InteractionContext,
        user: int,
        reason: str
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

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

        if not await self.__member_data_provider.is_member(context.server_id, user_id):
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("user_not_found_error"))
            )

        await self.__warn_manager.warn_user(context.server_id, user_id, reason, context.author_id)

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.warn_user_workflow.user_warned_dm",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name,
                        "reason": reason
                    }
                )
            )

        return UserWarnedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.warn_user_workflow.user_warned",
                    {
                        "user_id": user_id,
                        "reason": reason
                    }
                ),
                suppress_user_mentions=True
            )
        )

    @moderation_menu_item(
        title="Warn",
        menu_type=MenuType.USER,
        priority=1,
        required_moderator_permissions=ModeratorPermission.WARN_USERS
    )
    async def warn_user_via_menu_item(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerUserInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        if not await self.__member_data_provider.is_member(context.server_id, context.target_user_id):
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("user_not_found_error"))
            )

        await self.__warn_manager.warn_user(context.server_id, context.target_user_id, "Issued via menu item", context.author_id)

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                context.target_user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.warn_user_workflow.user_warned_dm_no_reason",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name
                    }
                )
            )

        return UserWarnedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.warn_user_workflow.user_warned_no_reason",
                    { "user_id": context.target_user_id }
                ),
                suppress_user_mentions=True
            )
        )
