import contextlib
from datetime import timedelta

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers.managers import SILENCE_DURATION_MAX, IUserManager
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import MenuType, OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import (
    ServerChatInteractionContext, ServerUserInteractionContext
)
from holobot.extensions.moderation.enums import ModeratorPermission
from holobot.sdk.chrono import InvalidInputError, parse_interval
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import textify_timedelta
from .interactables.decorators import moderation_command, moderation_menu_item
from .responses import UserMutedResponse as UserMutedInteractionResponse
from .responses.menu_item_responses import UserMutedResponse as UserMutedMenuItemResponse

_MIN_MUTE_DURATION = timedelta(seconds=30)
_MENU_ITEM_MUTE_DURATION = timedelta(minutes=15)

@injectable(IWorkflow)
class MuteUserWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        messaging: IMessaging,
        user_manager: IUserManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(MuteUserWorkflow)
        self.__messaging = messaging
        self.__user_manager = user_manager

    @moderation_command(
        description="Mutes a user.",
        name="mute",
        group_name="moderation",
        options=(
            Option("user", "The user to mute.", OptionType.USER),
            Option("reason", "The reason of the punishment."),
            Option("duration", "The duration after which to lift the mute. Eg. 1h or 30m.", is_mandatory=False)
        ),
        required_moderator_permissions=ModeratorPermission.MUTE_USERS
    )
    async def mute_user_via_command(
        self,
        context: InteractionContext,
        user: int,
        reason: str,
        duration: str | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        user_id = user
        reason = reason.strip()
        try:
            mute_duration = parse_interval(duration.strip()) if duration else None
        except (ArgumentOutOfRangeError, InvalidInputError):
            return self._reply(
                content=self.__i18n_provider.get("extensions.moderation.invalid_time_input_error")
            )

        if mute_duration and mute_duration < _MIN_MUTE_DURATION:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.moderation.duration_out_of_range_error",
                    { "min": textify_timedelta(_MIN_MUTE_DURATION), "max": SILENCE_DURATION_MAX }
                )
            )

        try:
            await self.__user_manager.silence_user(context.server_id, user_id, mute_duration)
        except ArgumentOutOfRangeError as error:
            if error.argument_name == "reason":
                return self._reply(
                    content=self.__i18n_provider.get(
                        "extensions.moderation.reason_out_of_range_error",
                        { "min": error.lower_bound, "max": error.upper_bound }
                    )
                )
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.moderation.duration_out_of_range_error",
                    { "min": error.lower_bound, "max": error.upper_bound }
                )
            )
        except UserNotFoundError:
            return self._reply(content=self.__i18n_provider.get("user_not_found_error"))
        except ForbiddenError as error:
            self.__logger.debug("Failed to mute user.", exception=error)
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.moderation.mute_user_workflow.cannot_mute_user_error",
                    { "user_id": user_id }
                ),
                suppress_user_mentions=True
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
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerUserInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        try:
            await self.__user_manager.silence_user(
                context.server_id,
                context.target_user_id,
                _MENU_ITEM_MUTE_DURATION
            )
        except UserNotFoundError:
            return self._reply(content=self.__i18n_provider.get("user_not_found_error"))
        except ForbiddenError:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.moderation.mute_user_workflow.cannot_mute_user_error",
                    { "user_id": context.target_user_id }
                ),
                suppress_user_mentions=True
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
