from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Command, Interactable
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.extensions.admin import CommandRuleManagerInterface
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflowExecutionRule)
class HaltDisabledCommandsRule(IWorkflowExecutionRule):
    def __init__(self, command_rule_manager: CommandRuleManagerInterface) -> None:
        super().__init__()
        self.__rule_manager: CommandRuleManagerInterface = command_rule_manager

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> bool:
        if isinstance(interactable, Command) and isinstance(context, ServerChatInteractionContext):
            return not await self.__rule_manager.can_execute(
                context.server_id,
                context.channel_id,
                interactable.group_name,
                interactable.subgroup_name,
                interactable.name
            )
        return False
