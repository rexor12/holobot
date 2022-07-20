from .. import AlertManagerInterface
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class RemoveAllAlarmsWorkflow(WorkflowBase):
    def __init__(self, alert_manager: AlertManagerInterface) -> None:
        super().__init__()
        self.__alert_manager: AlertManagerInterface = alert_manager

    @command(
        description="Removes ALL of your alarms.",
        name="removeall",
        group_name="crypto",
        subgroup_name="alarm"
    )
    async def remove_all_alarms(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        await self.__alert_manager.remove_all(context.author_id)
        return InteractionResponse(
            action=ReplyAction(content="All of your alarms have been removed.")
        )
