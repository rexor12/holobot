from discord_slash.context import SlashContext
from holobot.discord.sdk.commands import CommandInterface, CommandExecutionRuleInterface
from holobot.discord.sdk.utils import has_channel_permission
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandExecutionRuleInterface)
class HasRequiredPermissionRule(CommandExecutionRuleInterface):
    async def should_halt(self, command: CommandInterface, context: SlashContext) -> bool:
        return not has_channel_permission(context, context.author, command.required_permissions)
