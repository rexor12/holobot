from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.models import (
    ServerChatInteractionContext, ServerMessageInteractionContext, ServerUserInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.sdk.ioc.decorators import injectable

VALID_CONTEXTS = (
    ServerChatInteractionContext,
    ServerMessageInteractionContext,
    ServerUserInteractionContext
)

@injectable(IWorkflowExecutionRule)
class IsInteractableAvailableForServerRule(IWorkflowExecutionRule):
    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> bool:
        if not isinstance(context, VALID_CONTEXTS):
            return False

        return (
            len(interactable.server_ids) > 0
            and context.server_id not in interactable.server_ids
        )
