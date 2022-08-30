from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.models import (
    ServerChatInteractionContext, ServerMessageInteractionContext, ServerUserInteractionContext
)
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.extensions.moderation.managers import IPermissionManager
from holobot.extensions.moderation.workflows.interactables import (
    ModerationCommand, ModerationComponent, ModerationMenuItem
)
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflowExecutionRule)
class CheckModeratorPermissionRule(IWorkflowExecutionRule):
    def __init__(self, permission_manager: IPermissionManager) -> None:
        super().__init__()
        self.__permission_manager: IPermissionManager = permission_manager

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> tuple[bool, str | None]:
        if (
            not isinstance(interactable, (ModerationCommand, ModerationComponent, ModerationMenuItem))
            or not isinstance(context, (ServerChatInteractionContext, ServerMessageInteractionContext, ServerUserInteractionContext))
        ):
            return (False, None)

        return (
            not await self.__permission_manager.has_permissions(
                context.server_id,
                context.author_id,
                interactable.required_moderator_permissions
            ),
            None
        )
