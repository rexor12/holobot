from holobot.discord.sdk.commands import CommandInterface, CommandExecutionRuleInterface
from holobot.discord.sdk.commands.models import ServerChatInteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandExecutionRuleInterface)
class HasRequiredPermissionRule(CommandExecutionRuleInterface):
    def __init__(self, member_data_provider: IMemberDataProvider) -> None:
        super().__init__()
        self.__member_data_provider: IMemberDataProvider = member_data_provider

    async def should_halt(self, command: CommandInterface, context: ServerChatInteractionContext) -> bool:
        permissions = self.__member_data_provider.get_member_permissions(
            context.server_id,
            context.channel_id,
            context.author_id
        )
        return not command.required_permissions in permissions
