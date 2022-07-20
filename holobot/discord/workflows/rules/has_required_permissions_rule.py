from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext, ServerUserInteractionContext
from holobot.discord.sdk.workflows.rules import IWorkflowExecutionRule
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflowExecutionRule)
class HasRequiredPermissionsRule(IWorkflowExecutionRule):
    def __init__(self, member_data_provider: IMemberDataProvider) -> None:
        super().__init__()
        self.__member_data_provider: IMemberDataProvider = member_data_provider

    async def should_halt(
        self,
        workflow: IWorkflow,
        interactable: Interactable,
        context: InteractionContext
    ) -> bool:
        if not isinstance(context, (ServerChatInteractionContext, ServerUserInteractionContext)):
            return False

        permissions = self.__member_data_provider.get_member_permissions(
            context.server_id,
            context.channel_id,
            context.author_id
        )

        return (workflow.required_permissions | interactable.required_permissions) not in permissions