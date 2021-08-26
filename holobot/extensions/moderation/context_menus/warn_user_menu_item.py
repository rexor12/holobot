from .moderation_menu_item_base import ModerationMenuItemBase
from .responses import UserWarnedResponse
from ..enums import ModeratorPermission
from ..managers import IWarnManager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.context_menus import IMenuItem
from holobot.discord.sdk.context_menus.models import MenuItemResponse, ServerUserInteractionContext
from holobot.discord.sdk.exceptions import ForbiddenError
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IMenuItem)
class WarnUserMenuItem(ModerationMenuItemBase):
    def __init__(self, member_data_provider: IMemberDataProvider, messaging: IMessaging, warn_manager: IWarnManager) -> None:
        super().__init__("Warn user")
        self.required_moderator_permissions = ModeratorPermission.WARN_USERS
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__messaging: IMessaging = messaging
        self.__warn_manager: IWarnManager = warn_manager

    async def execute(self, context: ServerUserInteractionContext, **kwargs) -> MenuItemResponse:
        if not self.__member_data_provider.is_member(context.server_id, context.target_user_id):
            return MenuItemResponse(
                action=ReplyAction(content="The user you mentioned cannot be found.")
            )

        await self.__warn_manager.warn_user(context.server_id, context.target_user_id, "Issued via menu item", str(context.author_id))

        try:
            await self.__messaging.send_private_message(context.target_user_id, f"You have been warned in {context.server_name} by {context.author_name}. Maybe you should behave yourself.")
        except ForbiddenError:
            pass

        await reply(context, f"<@{context.target_user_id}> has been warned.")
        return UserWarnedResponse(
            author_id=str(context.author_id),
            user_id=context.target_user_id
        )
