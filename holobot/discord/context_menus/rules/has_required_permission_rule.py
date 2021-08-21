from discord_slash.context import MenuContext
from holobot.discord.sdk.context_menus import IMenuItem, IMenuItemExecutionRule
from holobot.discord.sdk.utils import has_channel_permission
from holobot.sdk.ioc.decorators import injectable

@injectable(IMenuItemExecutionRule)
class HasRequiredPermissionRule(IMenuItemExecutionRule):
    async def should_halt(self, menu_item: IMenuItem, context: MenuContext) -> bool:
        return not has_channel_permission(context, context.author, menu_item.required_permissions)
