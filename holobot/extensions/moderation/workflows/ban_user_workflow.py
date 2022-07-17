from typing import Optional

import contextlib

from .interactables.decorators import moderation_command, moderation_menu_item
from .responses import UserBannedResponse as UserBannedInteractionResponse
from .responses.menu_item_responses import UserBannedResponse as UserBannedMenuItemResponse
from .. import IConfigProvider
from ..enums import ModeratorPermission
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.servers.managers import IUserManager
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import MenuType, OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext, ServerUserInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class BanUserWorkflow(WorkflowBase):
    def __init__(
        self,
        config_provider: IConfigProvider,
        messaging: IMessaging,
        user_manager: IUserManager
    ) -> None:
        super().__init__()
        self.__config_provider: IConfigProvider = config_provider
        self.__messaging: IMessaging = messaging
        self.__user_manager: IUserManager = user_manager

    @moderation_command(
        description="Bans a user from the server. The user cannot rejoin until the ban is lifted.",
        name="ban",
        group_name="moderation",
        options=(
            Option("user", "The mention of the user to ban."),
            Option("reason", "The reason of the punishment."),
            Option("days", "If specified, the previous N days' messages are also removed.", OptionType.INTEGER, False)
        ),
        required_moderator_permissions=ModeratorPermission.BAN_USERS
    )
    async def ban_user_via_command(
        self,
        context: ServerChatInteractionContext,
        user: str,
        reason: str,
        days: Optional[int] = None
    ) -> InteractionResponse:
        user = user.strip()
        reason = reason.strip()
        if (user_id := get_user_id(user)) is None:
            return InteractionResponse(
                action=ReplyAction(content="You must mention a user correctly.")
            )
        days = days if days is not None else 0
        if days < 0 or days > 7:
            return InteractionResponse(
                action=ReplyAction(content="The days parameter's value must be between 0 and 7. If omitted, no messages are deleted.")
            )
        reason_length_range = self.__config_provider.get_reason_length_range()
        if len(reason) not in reason_length_range:
            return InteractionResponse(
                action=ReplyAction(content=f"The reason parameter's length must be between {reason_length_range.lower_bound} and {reason_length_range.upper_bound}.")
            )

        try:
            await self.__user_manager.ban_user(context.server_id, user_id, reason, days)
        except UserNotFoundError:
            return InteractionResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )
        except ForbiddenError:
            return InteractionResponse(
                action=ReplyAction(content=(
                    "I cannot ban the user.\n"
                    "Have you given me user management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(user_id, f"You have been banned from {context.server_name} by {context.author_name} with the reason '{reason}'. I'm sorry this happened to you.")

        return UserBannedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            action=ReplyAction(content=f"<@{user_id}> has been banned. Reason: {reason}")
        )

    @moderation_menu_item(
        title="Ban",
        menu_type=MenuType.USER,
        priority=5,
        required_moderator_permissions=ModeratorPermission.BAN_USERS
    )
    async def ban_user_via_menu_item(
        self,
        context: ServerUserInteractionContext
    ) -> InteractionResponse:
        try:
            await self.__user_manager.ban_user(context.server_id, context.target_user_id, "Issued via menu item")
        except UserNotFoundError:
            return InteractionResponse(
                action=ReplyAction(
                    content="The specified user cannot be found."
                )
            )
        except ForbiddenError:
            return InteractionResponse(
                action=ReplyAction(content=(
                    "I cannot kick the user.\n"
                    "Have you given me user management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(context.target_user_id, f"You have been banned from {context.server_name} by {context.author_name}. I'm sorry this happened to you.")

        return UserBannedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=f"<@{context.target_user_id}> has been banned."
            )
        )
