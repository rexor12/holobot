from .. import CommandRuleManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveCommandRuleCommand(CommandBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__("removerule")
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Removes the specified command rule."
        self.options = [
            Option("identifier", "The identifier of the rule.", OptionType.INTEGER)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        
    async def execute(self, context: ServerChatInteractionContext, identifier: int) -> CommandResponse:
        await self.__command_rule_manager.remove_rule(identifier)
        return CommandResponse(
            action=ReplyAction(content="The rule has been removed.")
        )
