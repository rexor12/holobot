from typing import Protocol

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.iworkflow import IWorkflow

class IWorkflowExecutionRule(Protocol):
    """Interface for a workflow execution rule.

    A rule is responsible for determining if a workflow's execution should be interrupted.
    """

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> tuple[bool, str | None]:
        """Determines if the specified interaction's execution should be stopped.

        :param workflow: The workflow the interactable belongs to.
        :type workflow: IWorkflow
        :param interactable: The currently executing interactable.
        :type interactable: InteractableRegistration
        :param context: The current interaction context.
        :type context: InteractionContext
        :return: True, if the interaction's execution should be stopped. An optional response message may be returned.
        :rtype: tuple[bool | None]
        """
        ...
