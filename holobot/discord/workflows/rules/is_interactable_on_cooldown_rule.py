from datetime import timedelta

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.models import (
    ServerChatInteractionContext, ServerMessageInteractionContext, ServerUserInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.discord.workflows import IInvocationTracker
from holobot.discord.workflows.utils import get_entity_id
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import utcnow

_SERVER_CONTEXTS = (
    ServerChatInteractionContext,
    ServerMessageInteractionContext,
    ServerUserInteractionContext
)

@injectable(IWorkflowExecutionRule)
class IsInteractableOnCooldownRule(IWorkflowExecutionRule):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        invocation_tracker: IInvocationTracker
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__invocation_tracker = invocation_tracker

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> tuple[bool, str | None]:
        if not interactable.cooldown:
            return (False, None)

        if not (entity_id := IsInteractableOnCooldownRule.__get_entity_id(interactable, context)):
            return (False, None)

        duration = timedelta(seconds=interactable.cooldown.duration)
        last_invocation = await self.__invocation_tracker.update_invocation(
            interactable.cooldown.entity_type,
            entity_id,
            utcnow(),
            duration
        )
        if not last_invocation:
            return (False, None)

        time_left = (last_invocation + duration - utcnow()).total_seconds()

        return (
            True,
            self.__i18n_provider.get(
                interactable.cooldown.message or "interactions.cooldown_error",
                { "seconds_left": time_left }
            )
        ) if time_left > 0 else (False, None)

    # NOTE: Threads share their cooldowns with their parent channels.
    @staticmethod
    def __get_entity_id(
        interactable: Interactable,
        context: InteractionContext
    ) -> str | None:
        server_id, channel_id = (
            (context.server_id, context.channel_id)
            if isinstance(context, _SERVER_CONTEXTS)
            else (None, None)
        )

        return get_entity_id(interactable, server_id, channel_id, context.author_id)
