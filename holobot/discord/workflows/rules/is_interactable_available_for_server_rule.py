from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.models import (
    ServerChatInteractionContext, ServerMessageInteractionContext, ServerUserInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

VALID_CONTEXTS = (
    ServerChatInteractionContext,
    ServerMessageInteractionContext,
    ServerUserInteractionContext
)

@injectable(IWorkflowExecutionRule)
class IsInteractableAvailableForServerRule(IWorkflowExecutionRule):
    def __init__(
        self,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> tuple[bool, str | None]:
        if not isinstance(context, VALID_CONTEXTS):
            return (False, None)

        return (
            len(interactable.server_ids) > 0 and context.server_id not in interactable.server_ids,
            self.__i18n_provider.get("interactions.not_available_for_server_error")
        )
