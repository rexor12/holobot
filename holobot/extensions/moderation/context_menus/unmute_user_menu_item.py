from .moderation_menu_item_base import ModerationMenuItemBase
from .responses import UserUnmutedResponse
from ..enums import ModeratorPermission
from ..managers import IMuteManager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.context_menus import IMenuItem
from holobot.discord.sdk.context_menus.models import MenuItemResponse, ServerUserInteractionContext
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.sdk.ioc.decorators import injectable

@injectable(IMenuItem)
class UnmuteUserMenuItem(ModerationMenuItemBase):
    def __init__(self, messaging: IMessaging, mute_manager: IMuteManager) -> None:
        super().__init__("Unmute user")
        self.required_moderator_permissions = ModeratorPermission.MUTE_USERS
        self.__messaging: IMessaging = messaging
        self.__mute_manager: IMuteManager = mute_manager

    async def execute(self, context: ServerUserInteractionContext, **kwargs) -> MenuItemResponse:
        try:
            await self.__mute_manager.unmute_user(context.server_id, context.target_user_id)
        except UserNotFoundError:
            return MenuItemResponse(
                action=ReplyAction(
                    content="The specified user cannot be found."
                )
            )
        except ForbiddenError:
            return MenuItemResponse(
                action=ReplyAction(
                    content=(
                    "I cannot remove the 'Muted' role.\n"
                    "Have you given me role management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        try:
            await self.__messaging.send_private_message(context.target_user_id, f"You have been unmuted in {context.server_name} by {context.author_name}. Make sure you behave next time.")
        except ForbiddenError:
            pass

        return UserUnmutedResponse(
            author_id=str(context.author_id),
            user_id=context.target_user_id,
            action=ReplyAction(
                content=f"<@{context.target_user_id}> has been unmuted."
            )
        )
