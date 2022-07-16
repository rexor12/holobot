from abc import ABCMeta, abstractmethod

from ..iworkflow import IWorkflow
from ..interactables import Interactable
from holobot.discord.sdk.models import InteractionContext

class IWorkflowExecutionRule(metaclass=ABCMeta):
    """Interface for a workflow execution rule.

    A rule is responsible for determining if a workflow's execution should be interrupted.
    """

    @abstractmethod
    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> bool:
        """Determines if the specified interaction's execution should be stopped.

        :param workflow: The workflow the interactable belongs to.
        :type workflow: IWorkflow
        :param interactable: The currently executing interactable.
        :type interactable: InteractableRegistration
        :param context: The current interaction context.
        :type context: InteractionContext
        :return: True, if the interaction's execution should be stopped.
        :rtype: bool
        """
        ...
