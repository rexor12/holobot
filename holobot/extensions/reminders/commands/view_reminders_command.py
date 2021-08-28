from .. import ReminderManagerInterface
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.components import Pager
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional

@injectable(CommandInterface)
class ViewRemindersCommand(CommandBase):
    def __init__(self, log: LogInterface, messaging: IMessaging, reminder_manager: ReminderManagerInterface) -> None:
        super().__init__("view")
        self.__log: LogInterface = log.with_name("Reminders", "ViewRemindersCommand")
        self.__messaging: IMessaging = messaging
        self.__reminder_manager: ReminderManagerInterface = reminder_manager
        self.group_name = "reminder"
        self.description = "Displays your reminders."

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        await Pager(self.__messaging, self.__log, context, self.__create_reminder_embed)
        return CommandResponse()

    async def __create_reminder_embed(self, context: ServerChatInteractionContext, page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        reminders = await self.__reminder_manager.get_by_user(context.author_id, start_offset, page_size)
        if len(reminders) == 0:
            return None
        
        embed = Embed(
            title="Reminders",
            description=f"Reminders of {context.author_id}.",
            footer=EmbedFooter("Use the reminder's number for removal.")
        )
        for reminder in reminders:
            embed.fields.append(EmbedField(
                name=f"#{reminder.id}",
                value=(
                    f"> Message: {reminder.message}\n"
                    f"> Next trigger: {reminder.next_trigger:%I:%M:%S %p, %m/%d/%Y} UTC\n"
                    f"> Repeats: {'yes' if reminder.is_repeating else 'no'}"
                ),
                is_inline=False
            ))

        return embed
