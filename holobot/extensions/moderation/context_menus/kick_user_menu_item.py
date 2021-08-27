from .moderation_menu_item_base import ModerationMenuItemBase
from .responses import UserKickedResponse
from ..enums import ModeratorPermission
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.context_menus import IMenuItem
from holobot.discord.sdk.context_menus.models import MenuItemResponse, ServerUserInteractionContext
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.servers.managers import IUserManager
from holobot.sdk.ioc.decorators import injectable

@injectable(IMenuItem)
class KickUserMenuItem(ModerationMenuItemBase):
    def __init__(self, messaging: IMessaging, user_manager: IUserManager) -> None:
        super().__init__("Kick user")
        self.required_moderator_permissions = ModeratorPermission.KICK_USERS
        self.__messaging: IMessaging = messaging
        self.__user_manager: IUserManager = user_manager

    async def execute(self, context: ServerUserInteractionContext, **kwargs) -> MenuItemResponse:
        try:
            await self.__user_manager.kick_user(context.server_id, context.target_user_id, "Issued via menu item")
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
                    "I cannot kick the user.\n"
                    "Have you given me user management permissions?\n"
                    "Do they have a role ranking higher than mine?"
                ))
            )

        try:
            await self.__messaging.send_private_message(context.target_user_id, f"You have been kicked from {context.server_name} by {context.author_name}. I'm sorry this happened to you.")
        except ForbiddenError:
            pass

        return UserKickedResponse(
            author_id=str(context.author_id),
            user_id=context.target_user_id,
            action=ReplyAction(
                content=f"<@{context.target_user_id}> has been kicked."
            )
        )
