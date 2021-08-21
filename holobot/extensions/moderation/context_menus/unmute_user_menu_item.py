from .moderation_menu_item_base import ModerationMenuItemBase
from .responses import UserUnmutedResponse
from ..enums import ModeratorPermission
from ..managers import IMuteManager
from discord_slash.context import MenuContext
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.context_menus import IMenuItem, MenuItemResponse
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(IMenuItem)
class UnmuteUserMenuItem(ModerationMenuItemBase):
    def __init__(self, messaging: IMessaging, mute_manager: IMuteManager) -> None:
        super().__init__("Unmute user")
        self.required_moderator_permissions = ModeratorPermission.MUTE_USERS
        self.__messaging: IMessaging = messaging
        self.__mute_manager: IMuteManager = mute_manager

    async def execute(self, context: MenuContext, **kwargs) -> MenuItemResponse:
        user_id: Optional[int] = context.target_id
        if not user_id:
            await reply(context, "Invalid user identifier specified. This may be because of an internal error. Please, try again later or contact the administrator.")
            return MenuItemResponse()
        if context.guild is None:
            await reply(context, "You may use this menu item in a server only.")
            return MenuItemResponse()

        try:
            await self.__mute_manager.unmute_user(str(context.guild_id), str(user_id))
        except UserNotFoundError:
            await reply(context, "The specified user cannot be found.")
            return MenuItemResponse()
        except ForbiddenError:
            await reply(context, (
                "I cannot remove the 'Muted' role.\n"
                "Have you given me role management permissions?\n"
                "Do they have a role ranking higher than mine?"
            ))
            return MenuItemResponse()

        await reply(context, f"<@{user_id}> has been unmuted.")
        return UserUnmutedResponse(
            author_id=str(context.author_id),
            user_id=str(user_id)
        )
