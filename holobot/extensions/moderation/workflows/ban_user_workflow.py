import contextlib

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.models import InteractionContext
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
from .responses import UserBannedResponse as UserBannedInteractionResponse
from .responses.menu_item_responses import UserBannedResponse as UserBannedMenuItemResponse

_MIN_DAYS = 0
_MAX_DAYS = 7

@injectable(IWorkflow)
class BanUserWorkflow(WorkflowBase):
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
        description="Bans a user from the server. The user cannot rejoin until the ban is lifted.",
        name="ban",
        group_name="moderation",
        options=(
            Option("user", "The user to ban.", OptionType.USER),
            Option("reason", "The reason of the punishment."),
            Option("days", "If specified, the previous N days' messages are also removed.", OptionType.INTEGER, False)
        ),
        required_moderator_permissions=ModeratorPermission.BAN_USERS
    )
    async def ban_user_via_command(
        self,
        context: InteractionContext,
        user: int,
        reason: str,
        days: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        user_id = user
        reason = reason.strip()

        days = days if days is not None else 0
        if days < _MIN_DAYS or days > _MAX_DAYS:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.moderation.ban_user_workflow.days_out_of_range_error",
                    { "min": _MIN_DAYS, "max": _MAX_DAYS }
                ))
            )

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
            await self.__user_manager.ban_user(context.server_id, user_id, reason, days)
        except UserNotFoundError:
            return InteractionResponse(action=ReplyAction(
                content=self.__i18n_provider.get("user_not_found_error")
            ))
        except ForbiddenError:
            return InteractionResponse(action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.ban_user_workflow.cannot_ban_user_error",
                    { "user_id": user_id }
                ),
                suppress_user_mentions=True
            ))

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.ban_user_workflow.user_banned_dm",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name,
                        "reason": reason
                    }
                )
            )

        return UserBannedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.ban_user_workflow.user_banned",
                    {
                        "user_id": user_id,
                        "reason": reason
                    }
                ),
                suppress_user_mentions=True
            )
        )

    @moderation_menu_item(
        title="Ban",
        menu_type=MenuType.USER,
        priority=5,
        required_moderator_permissions=ModeratorPermission.BAN_USERS
    )
    async def ban_user_via_menu_item(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerUserInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        try:
            await self.__user_manager.ban_user(context.server_id, context.target_user_id, "Issued via menu item")
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
                        "extensions.moderation.ban_user_workflow.cannot_ban_user_error",
                        { "user_id": context.target_user_id }
                    ),
                    suppress_user_mentions=True
                )
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                context.target_user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.ban_user_workflow.user_banned_dm_no_reason",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name
                    }
                )
            )

        return UserBannedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.ban_user_workflow.user_banned_no_reason",
                    { "user_id": context.target_user_id }
                ),
                suppress_user_mentions=True
            )
        )
