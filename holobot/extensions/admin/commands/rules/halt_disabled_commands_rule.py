from discord_slash import SlashContext
from holobot.discord.sdk.commands import CommandInterface, CommandExecutionRuleInterface
from holobot.extensions.admin import CommandRuleManagerInterface
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandExecutionRuleInterface)
class HaltDisabledCommandsRule(CommandExecutionRuleInterface):
    def __init__(self, command_rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__()
        self.__rule_manager: CommandRuleManagerInterface = command_rule_manager

    async def should_halt(self, command: CommandInterface, context: SlashContext) -> bool:
        return await self.__is_command_disabled(command, context)
    
    async def __is_command_disabled(self, command: CommandInterface, context: SlashContext) -> bool:
        return not await self.__rule_manager.can_execute(
            str(context.guild_id),
            str(context.channel_id),
            command.group_name,
            command.subgroup_name,
            command.name
        )
