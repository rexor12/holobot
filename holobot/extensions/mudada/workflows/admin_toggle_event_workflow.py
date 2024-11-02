from enum import IntEnum

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import (
    MUDADA_FEATURE_NAME, VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME
)
from holobot.extensions.mudada.models.feature_state import FeatureState
from holobot.extensions.mudada.repositories import IFeatureStateRepository
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.database.repositories import IEntityCache
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

class EventType(IntEnum):
    UNKNOWN = 0
    VALENTINES2024 = 1

EVENT_TYPE_TO_FEATURE_STATE_NAME_MAP: dict[EventType, str] = {
    EventType.VALENTINES2024: VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME
}

@injectable(IWorkflow)
class AdminToggleEventWorkflow(WorkflowBase):
    def __init__(
        self,
        entity_cache: IEntityCache,
        feature_state_repository: IFeatureStateRepository,
        i18n_provider: II18nProvider,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__entity_cache = entity_cache
        self.__feature_state_repository = feature_state_repository
        self.__i18n = i18n_provider
        self.__unit_of_work_provider = unit_of_work_provider

    @command(
        group_name="mudada",
        subgroup_name="admin",
        name="toggleevent",
        description="Turns a specific event on or off.",
        options=(
            Option(
                "event",
                "The event to turn on or off.",
                OptionType.INTEGER,
                choices=(
                    Choice("Valentine's Day", EventType.VALENTINES2024),
                )
            ),
            Option("enabled", "The new state of the event.", OptionType.BOOLEAN)
        ),
        required_permissions=Permission.ADMINISTRATOR,
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def toggle_event(
        self,
        context: InteractionContext,
        event: int,
        enabled: bool
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        event_type = EventType(event)
        feature_state_name = EVENT_TYPE_TO_FEATURE_STATE_NAME_MAP[event_type]
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            feature_state = await self.__feature_state_repository.get(feature_state_name)
            if feature_state:
                feature_state.is_enabled = enabled
                await self.__feature_state_repository.update(feature_state)
            else:
                feature_state = FeatureState(feature_state_name, enabled)
                await self.__feature_state_repository.add(feature_state)

            unit_of_work.complete()

        await self.__entity_cache.invalidate(FeatureState, feature_state_name)

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.admin_toggle_event_workflow.state_changed_successfully",
                {
                    "state": self.__i18n.get(
                        "extensions.mudada.admin_toggle_event_workflow.state_on"
                        if enabled
                        else "extensions.mudada.admin_toggle_event_workflow.state_off"
                    )
                }
            )
        )
