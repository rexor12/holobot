from .. import ReminderManagerInterface
from ..exceptions import InvalidReminderError
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(IWorkflow)
class RemoveReminderWorkflow(WorkflowBase):
    def __init__(self, log: LogInterface, reminder_manager: ReminderManagerInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Reminders", "RemoveReminderWorkflow")
        self.__reminder_manager: ReminderManagerInterface = reminder_manager

    @command(
        description="Removes a reminder.",
        name="remove",
        group_name="reminder",
        options=(
            Option("id", "The identifier of the reminder.", OptionType.INTEGER),
        )
    )
    async def remove_reminder(
        self,
        context: ServerChatInteractionContext,
        id: int
    ) -> InteractionResponse:
        try:
            await self.__reminder_manager.delete_reminder(context.author_id, id)
            self.__log.debug(f"Deleted a reminder. {{ UserId = {context.author_id}, ReminderId = {id} }}")
            return InteractionResponse(
                action=ReplyAction(
                    content="The reminder has been deleted."
                )
            )
        except InvalidReminderError:
            return InteractionResponse(
                action=ReplyAction(
                    content="That reminder doesn't exist or belong to you."
                )
            )
