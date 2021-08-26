from .. import ModerationMenuItemBase
from holobot.discord.sdk.context_menus import IMenuItem, IMenuItemExecutionRule
from holobot.discord.sdk.context_menus.models import ServerUserInteractionContext
from holobot.discord.sdk.models import InteractionContext
from holobot.extensions.moderation.managers import IPermissionManager
from holobot.sdk.ioc.decorators import injectable

@injectable(IMenuItemExecutionRule)
class CheckModeratorPermissionRule(IMenuItemExecutionRule):
    def __init__(self, permission_manager: IPermissionManager) -> None:
        super().__init__()
        self.__permission_manager: IPermissionManager = permission_manager

    async def should_halt(self, menu_item: IMenuItem, context: InteractionContext) -> bool:
        if not isinstance(context, ServerUserInteractionContext):
            return False

        if not isinstance(menu_item, ModerationMenuItemBase):
            return False

        return not await self.__permission_manager.has_permissions(
            context.server_id,
            context.author_id,
            menu_item.required_moderator_permissions
        )
