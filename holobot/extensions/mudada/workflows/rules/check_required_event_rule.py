from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.extensions.mudada.repositories import IFeatureStateRepository
from holobot.extensions.mudada.workflows.decorators.requires_event import REQUIRED_EVENT_NAME_KEY
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflowExecutionRule)
class CheckRequiredEventRule(IWorkflowExecutionRule):
    def __init__(
        self,
        feature_state_repository: IFeatureStateRepository,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__feature_state_repository = feature_state_repository
        self.__i18n = i18n_provider

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> tuple[bool, str | None]:
        required_event_name = interactable.extension_data.get(REQUIRED_EVENT_NAME_KEY)
        if not required_event_name:
            return (False, None)

        feature_state = await self.__feature_state_repository.get(required_event_name)
        if not feature_state or not feature_state.is_enabled:
            return (
                True,
                self.__i18n.get("extensions.mudada.inactive_event_error")
            )

        return (False, None)
