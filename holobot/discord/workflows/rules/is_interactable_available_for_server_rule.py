from holobot.discord.sdk.authorization import IAuthorizationDataProvider
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.models import (
    ServerChatInteractionContext, ServerMessageInteractionContext, ServerUserInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

RELEVANT_CONTEXTS = (
    ServerChatInteractionContext,
    ServerMessageInteractionContext,
    ServerUserInteractionContext
)

@injectable(IWorkflowExecutionRule)
class IsInteractableAvailableForServerRule(IWorkflowExecutionRule):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        authorization_data_provider: IAuthorizationDataProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__authorization_data_provider = authorization_data_provider

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> tuple[bool, str | None]:
        if not isinstance(context, RELEVANT_CONTEXTS):
            return (False, None)

        is_allowed = await self.__authorization_data_provider.is_server_authorized(
            interactable,
            context.server_id
        )
        if is_allowed:
            return (False, None)

        return (True, self.__i18n_provider.get("interactions.not_available_for_server_error"))
