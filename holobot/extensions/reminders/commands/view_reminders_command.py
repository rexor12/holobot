from .. import ReminderManagerInterface
from discord.embeds import Embed
from discord.ext.commands.context import Context
from discord_slash.context import SlashContext
from holobot.discord.components import DynamicPager
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.utils import get_author_id
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional, Union

@injectable(CommandInterface)
class ViewRemindersCommand(CommandBase):
    def __init__(self, log: LogInterface, messaging: IMessaging, reminder_manager: ReminderManagerInterface) -> None:
        super().__init__("view")
        self.__log: LogInterface = log.with_name("Reminders", "ViewRemindersCommand")
        self.__messaging: IMessaging = messaging
        self.__reminder_manager: ReminderManagerInterface = reminder_manager
        self.group_name = "reminder"
        self.description = "Displays your reminders."

    async def execute(self, context: SlashContext) -> CommandResponse:
        await DynamicPager(self.__messaging, self.__log, context, self.__create_reminder_embed)
        return CommandResponse()

    async def __create_reminder_embed(self, context: Union[Context, SlashContext], page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        reminders = await self.__reminder_manager.get_by_user(get_author_id(context), start_offset, page_size)
        if len(reminders) == 0:
            return None
        
        embed = Embed(
            title="Reminders",
            description=f"Reminders of {context.author.mention}.",
            color=0xeb7d00
        ).set_footer(text="Use the reminder's number for removal.")
        for reminder in reminders:
            embed.add_field(
                name=f"#{reminder.id}",
                value=(
                    f"> Message: {reminder.message}\n"
                    f"> Next trigger: {reminder.next_trigger:%I:%M:%S %p, %m/%d/%Y} UTC\n"
                    f"> Repeats: {'yes' if reminder.is_repeating else 'no'}"
                ),
                inline=False
            )
        return embed
