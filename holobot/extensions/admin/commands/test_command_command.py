from .. import CommandRegistryInterface, CommandRuleManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.utils import get_channel_id_or_default
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class TestCommandCommand(CommandBase):
    def __init__(self, command_registry: CommandRegistryInterface, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__("test")
        self.__command_registry: CommandRegistryInterface = command_registry
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Checks if a command can be used in the current or the specified channel."
        self.options = [
            Option("command", "The specific command, such as \"roll\"."),
            Option("group", "The command group, such as \"admin\".", is_mandatory=False),
            Option("subgroup", "The command subgroup, such as \"commands\".", is_mandatory=False),
            Option("channel", "The channel to test.", is_mandatory=False)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        
    async def execute(self, context: ServerChatInteractionContext, command: str, group: Optional[str] = None, subgroup: Optional[str] = None, channel: Optional[str] = None) -> CommandResponse:
        if context.server_id is None:
            return CommandResponse(
                action=ReplyAction(content="Command rules can be defined in servers only.")
            )
        
        if not self.__command_registry.command_exists(command, group, subgroup):
            return CommandResponse(
                action=ReplyAction(content="The command you specified doesn't exist. Did you make a typo?")
            )

        channel_id = get_channel_id_or_default(channel, context.channel_id) if channel is not None else context.channel_id
        can_execute = await self.__command_rule_manager.can_execute(context.server_id, channel_id, group, subgroup, command)
        disabled_text = " NOT" if not can_execute else ""
        return CommandResponse(
            action=ReplyAction(content=f"The command CAN{disabled_text} be executed in <#{channel_id}>.")
        )
