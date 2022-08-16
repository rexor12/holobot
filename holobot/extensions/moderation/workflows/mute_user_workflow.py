
import contextlib

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import MenuType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import (
    ServerChatInteractionContext, ServerUserInteractionContext
)
from holobot.sdk.chrono import parse_interval
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from ..enums import ModeratorPermission
from ..managers import IMuteManager
from .interactables.decorators import moderation_command, moderation_menu_item
from .responses import UserMutedResponse as UserMutedInteractionResponse
from .responses.menu_item_responses import UserMutedResponse as UserMutedMenuItemResponse

@injectable(IWorkflow)
class MuteUserWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        messaging: IMessaging,
        mute_manager: IMuteManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(MuteUserWorkflow)
        self.__messaging = messaging
        self.__mute_manager = mute_manager

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
        duration: str | None = None
    ) -> InteractionResponse:
        user = user.strip()
        reason = reason.strip()
        mute_duration = parse_interval(duration.strip()) if duration is not None else None
        if (user_id := get_user_id(user)) is None:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("user_not_found_error"))
            )

        try:
            await self.__mute_manager.mute_user(context.server_id, user_id, reason, mute_duration)
        except ArgumentOutOfRangeError as error:
            if error.argument_name == "reason":
                return InteractionResponse(
                    action=ReplyAction(
                        content=self.__i18n_provider.get(
                            "extensions.moderation.reason_out_of_range_error",
                            { "min": error.lower_bound, "max": error.upper_bound }
                        )
                    )
                )
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.duration_out_of_range_error",
                        { "min": error.lower_bound, "max": error.upper_bound }
                    )
                )
            )
        except UserNotFoundError:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get("user_not_found_error"))
            )
        except ForbiddenError as error:
            self.__logger.error("Failed to mute user.", error)
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.mute_user_workflow.cannot_mute_user_error",
                        { "user_id": user_id }
                    ),
                    suppress_user_mentions=True
                )
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.mute_user_workflow.user_muted_dm",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name,
                        "reason": reason
                    }
                )
            )

        return UserMutedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            duration=mute_duration,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.mute_user_workflow.user_muted",
                    {
                        "user_id": user_id,
                        "reason": reason
                    }
                ),
                suppress_user_mentions=True
            )
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
                    content=self.__i18n_provider.get("user_not_found_error")
                )
            )
        except ForbiddenError:
            return InteractionResponse(
                action=ReplyAction(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.mute_user_workflow.cannot_mute_user_error",
                        { "user_id": context.target_user_id }
                    ),
                    suppress_user_mentions=True
                )
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(
                context.target_user_id,
                self.__i18n_provider.get(
                    "extensions.moderation.mute_user_workflow.user_muted_dm_no_reason",
                    {
                        "user_name": context.author_name,
                        "server_name": context.server_name
                    }
                )
            )

        return UserMutedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=self.__i18n_provider.get(
                    "extensions.moderation.mute_user_workflow.user_muted_no_reason",
                    { "user_id": context.target_user_id }
                ),
                suppress_user_mentions=True
            )
        )
