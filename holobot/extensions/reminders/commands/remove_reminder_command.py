from .. import ReminderManagerInterface
from ..exceptions import InvalidReminderError
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(CommandInterface)
class RemoveReminderCommand(CommandBase):
    def __init__(self, log: LogInterface, reminder_manager: ReminderManagerInterface) -> None:
        super().__init__("remove")
        self.__log: LogInterface = log.with_name("Reminders", "RemoveReminderCommand")
        self.__reminder_manager: ReminderManagerInterface = reminder_manager
        self.group_name = "reminder"
        self.description = "Removes a reminder."
        self.options = [
            Option("id", "The identifier of the reminder.", OptionType.INTEGER)
        ]

    async def execute(self, context: ServerChatInteractionContext, id: int) -> CommandResponse:
        try:
            await self.__reminder_manager.delete_reminder(context.author_id, id)
            self.__log.debug(f"Deleted a reminder. {{ UserId = {context.author_id}, ReminderId = {id} }}")
            return CommandResponse(
                action=ReplyAction(
                    content="The reminder has been deleted."
                )
            )
        except InvalidReminderError:
            return CommandResponse(
                action=ReplyAction(
                    content="That reminder doesn't exist or belong to you."
                )
            )
