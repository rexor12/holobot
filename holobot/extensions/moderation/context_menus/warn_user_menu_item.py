from .moderation_menu_item_base import ModerationMenuItemBase
from .responses import UserWarnedResponse
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from discord.member import Member
from discord_slash.context import MenuContext
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.context_menus import IMenuItem, MenuItemResponse
from holobot.discord.sdk.exceptions import ForbiddenError, UserNotFoundError
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(IMenuItem)
class WarnUserMenuItem(ModerationMenuItemBase):
    def __init__(self, messaging: IMessaging, warn_manager: IWarnManager) -> None:
        super().__init__("Warn user")
        self.required_moderator_permissions = ModeratorPermission.WARN_USERS
        self.__messaging: IMessaging = messaging
        self.__warn_manager: IWarnManager = warn_manager

    async def execute(self, context: MenuContext, **kwargs) -> MenuItemResponse:
        user_id: Optional[int] = context.target_id
        if not user_id:
            await reply(context, "Invalid user identifier specified. This may be because of an internal error. Please, try again later or contact the administrator.")
            return MenuItemResponse()
        if context.guild is None:
            await reply(context, "You may use this menu item in a server only.")
            return MenuItemResponse()

        member = context.guild.get_member(int(user_id))
        if member is None:
            await reply(context, "The user you mentioned cannot be found.")
            return MenuItemResponse()
        if not isinstance(member, Member):
            await reply(context, "I'm sorry, but something went wrong internally. Please, try again later or contact your server administrator.")
            return MenuItemResponse()

        await self.__warn_manager.warn_user(str(context.guild_id), str(user_id), "Issued via menu item", str(context.author_id))

        try:
            await self.__messaging.send_dm(str(user_id), f"You have been warned in {context.guild.name} by {context.author.name}. Maybe you should behave yourself.")
        except ForbiddenError:
            pass

        await reply(context, f"<@{user_id}> has been warned.")
        return UserWarnedResponse(
            author_id=str(context.author_id),
            user_id=str(user_id)
        )
