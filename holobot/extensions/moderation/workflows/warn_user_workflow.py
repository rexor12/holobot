import contextlib

from .interactables.decorators import moderation_command, moderation_menu_item
from .responses import UserWarnedResponse as UserWarnedInteractionResponse
from .responses.menu_item_responses import UserWarnedResponse as UserWarnedMenuItemResponse
from .. import IConfigProvider
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.enums import MenuType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext, ServerUserInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class WarnUserWorkflow(WorkflowBase):
    def __init__(self, config_provider: IConfigProvider, member_data_provider: IMemberDataProvider, messaging: IMessaging, warn_manager: IWarnManager) -> None:
        super().__init__()
        self.__config_provider: IConfigProvider = config_provider
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__messaging: IMessaging = messaging
        self.__warn_manager: IWarnManager = warn_manager

    @moderation_command(
        description="Warns a user, giving them one warn strike.",
        name="warn",
        group_name="moderation",
        options=(
            Option("user", "The mention of the user to warn."),
            Option("reason", "The reason of the punishment.")
        ),
        required_moderator_permissions=ModeratorPermission.WARN_USERS
    )
    async def warn_user_via_command(
        self,
        context: ServerChatInteractionContext,
        user: str,
        reason: str
    ) -> InteractionResponse:
        user = user.strip()
        reason = reason.strip()
        if (user_id := get_user_id(user)) is None:
            return InteractionResponse(
                action=ReplyAction(
                    content="You must mention a user correctly."
                )
            )

        reason_length_range = self.__config_provider.get_reason_length_range()
        if len(reason) not in reason_length_range:
            return InteractionResponse(
                action=ReplyAction(
                    content=f"The reason parameter's length must be between {reason_length_range.lower_bound} and {reason_length_range.upper_bound}."
                )
            )

        if not self.__member_data_provider.is_member(context.server_id, user_id):
            return InteractionResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )

        await self.__warn_manager.warn_user(context.server_id, user_id, reason, context.author_id)

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(user_id, f"You have been warned in {context.server_name} by {context.author_name} with the reason '{reason}'. Maybe you should behave yourself.")

        return UserWarnedInteractionResponse(
            author_id=context.author_id,
            user_id=user_id,
            reason=reason,
            action=ReplyAction(
                content=f"<@{user_id}> has been warned. Reason: {reason}"
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
        context: ServerUserInteractionContext
    ) -> InteractionResponse:
        if not self.__member_data_provider.is_member(context.server_id, context.target_user_id):
            return InteractionResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )

        await self.__warn_manager.warn_user(context.server_id, context.target_user_id, "Issued via menu item", context.author_id)

        with contextlib.suppress(ForbiddenError):
            await self.__messaging.send_private_message(context.target_user_id, f"You have been warned in {context.server_name} by {context.author_name}. Maybe you should behave yourself.")

        return UserWarnedMenuItemResponse(
            author_id=context.author_id,
            user_id=context.target_user_id,
            action=ReplyAction(
                content=f"<@{context.target_user_id}> has been warned."
            )
        )
