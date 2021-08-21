from .. import ModerationMenuItemBase
from discord_slash.context import MenuContext
from holobot.discord.sdk.context_menus import IMenuItem, IMenuItemExecutionRule
from holobot.extensions.moderation.managers import IPermissionManager
from holobot.sdk.ioc.decorators import injectable

@injectable(IMenuItemExecutionRule)
class CheckModeratorPermissionRule(IMenuItemExecutionRule):
    def __init__(self, permission_manager: IPermissionManager) -> None:
        super().__init__()
        self.__permission_manager: IPermissionManager = permission_manager

    async def should_halt(self, menu_item: IMenuItem, context: MenuContext) -> bool:
        if not isinstance(menu_item, ModerationMenuItemBase):
            return False

        return not await self.__permission_manager.has_permissions(
            str(context.guild_id),
            str(context.author_id),
            menu_item.required_moderator_permissions
        )
