from discord_slash import SlashContext
from holobot.discord.sdk.commands import CommandInterface, CommandExecutionRuleInterface
from holobot.discord.sdk.utils import has_channel_permission
from holobot.extensions.admin import CommandRuleManagerInterface
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandExecutionRuleInterface)
class CommandExecutionRule(CommandExecutionRuleInterface):
    def __init__(self, command_rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__()
        self.__rule_manager: CommandRuleManagerInterface = command_rule_manager

    async def should_halt(self, command: CommandInterface, context: SlashContext) -> bool:
        return (await self.__is_command_disabled(command, context)
                or not has_channel_permission(context, context.author, command.required_permissions))
    
    async def __is_command_disabled(self, command: CommandInterface, context: SlashContext) -> bool:
        return not await self.__rule_manager.can_execute(
            str(context.guild_id),
            str(context.channel_id),
            command.group_name,
            command.subgroup_name,
            command.name
        )