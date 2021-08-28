from holobot.discord.sdk.context_menus import IMenuItem, IMenuItemExecutionRule
from holobot.discord.sdk.context_menus.models import ServerUserInteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IMenuItemExecutionRule)
class HasRequiredPermissionRule(IMenuItemExecutionRule):
    def __init__(self, member_data_provider: IMemberDataProvider) -> None:
        super().__init__()
        self.__member_data_provider: IMemberDataProvider = member_data_provider

    async def should_halt(self, menu_item: IMenuItem, context: ServerUserInteractionContext) -> bool:
        permissions = self.__member_data_provider.get_member_permissions(
            context.server_id,
            context.channel_id,
            context.author_id
        )
        return not menu_item.required_permissions in permissions
        
