from .. import ReminderManagerInterface
from ..exceptions import InvalidReminderError
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id, reply
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

@injectable(CommandInterface)
class RemoveReminderCommand(CommandBase):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__(services, "remove")
        self.__log: LogInterface = services.get(LogInterface).with_name("Reminders", "RemoveReminderCommand")
        self.__reminder_manager: ReminderManagerInterface = services.get(ReminderManagerInterface)
        self.group_name = "reminder"
        self.description = "Removes a reminder."
        self.options = [
            create_option("id", "The identifier of the reminder.", SlashCommandOptionType.INTEGER, True)
        ]

    async def execute(self, context: SlashContext, id: int) -> None:
        try:
            user_id = get_author_id(context)
            await self.__reminder_manager.delete_reminder(user_id, id)
            await reply(context, "The reminder has been deleted.")
            self.__log.debug(f"Deleted a reminder. {{ UserId = {user_id}, ReminderId = {id} }}")
        except InvalidReminderError:
            await reply(context, "That reminder doesn't exist or belong to you.")
