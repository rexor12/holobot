from .. import CommandRuleManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveAllCommandRulesCommand(CommandBase):
    def __init__(self, rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__("removeall")
        self.__command_rule_manager: CommandRuleManagerInterface = rule_manager
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Removes ALL command rules specified for this server."
        self.options = [
            Option("confirmation", "Type \"confirm\" if you are sure about this.")
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        
    async def execute(self, context: ServerChatInteractionContext, confirmation: str) -> CommandResponse:
        if confirmation != "confirm":
            return CommandResponse(
                action=ReplyAction(content="No rules have been removed. You must confirm your intention correctly.")
            )

        await self.__command_rule_manager.remove_rules_by_server(context.server_id)
        return CommandResponse(
            action=ReplyAction(content="ALL rules specified for this server have been removed.")
        )
