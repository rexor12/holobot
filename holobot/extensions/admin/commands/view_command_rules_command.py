from .. import CommandRuleManagerInterface
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import Embed, EmbedField
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional

@injectable(CommandInterface)
class ViewCommandRulesCommand(CommandBase):
    def __init__(self, command_manager: CommandRuleManagerInterface, log: LogInterface, messaging: IMessaging) -> None:
        super().__init__("viewrules")
        self.__command_manager: CommandRuleManagerInterface = command_manager
        self.__log: LogInterface = log.with_name("Admin", "ViewCommandRulesCommand")
        self.__messaging: IMessaging = messaging
        self.group_name = "admin"
        self.subgroup_name = "commands"
        self.description = "Lists the rules set on this server."
        self.options = [
            Option("group", "The name of the command group, such as \"admin\".", is_mandatory=False),
            Option("subgroup", "The name of the command sub-group, such as \"commands\" under \"admin\".", is_mandatory=False)
        ]
        self.required_permissions = Permission.ADMINISTRATOR
        
    async def execute(self, context: ServerChatInteractionContext, group: Optional[str] = None, subgroup: Optional[str] = None) -> CommandResponse:
        # if not group and subgroup:
        #     return CommandResponse(
        #         action=ReplyAction(content="You can specify a subgroup if and only if you specify a group, too.")
        #     )

        # async def create_filtered_embed(context: ServerChatInteractionContext, page: int, page_size: int) -> Optional[Embed]:
        #     start_offset = page * page_size
        #     rules = await self.__command_manager.get_rules_by_server(context.server_id, start_offset, page_size, group, subgroup)
        #     if len(rules) == 0:
        #         return None

        #     return Embed(
        #         title="Command rules",
        #         description="The list of command rules set on this server.",
        #         color=0xeb7d00,
        #         fields=[EmbedField(
        #             name=f"Rule #{rule.id}",
        #             value=rule.textify(),
        #             is_inline=False
        #         ) for rule in rules]
        #     )

        # await Pager(self.__messaging, self.__log, context, create_filtered_embed)
        # return CommandResponse()
        # TODO Implement paging.
        return CommandResponse(ReplyAction("Not implemented yet."))
