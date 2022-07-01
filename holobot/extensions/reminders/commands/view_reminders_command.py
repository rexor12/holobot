from .. import ReminderManagerInterface
from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.components import Paginator
from holobot.discord.sdk.components.models import (
    ComponentInteractionResponse, ComponentRegistration, PagerState
)
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Any, Union

DEFAULT_PAGE_SIZE = 5

@injectable(CommandInterface)
class ViewRemindersCommand(CommandBase):
    def __init__(self, log: LogInterface, reminder_manager: ReminderManagerInterface) -> None:
        super().__init__("view")
        self.__log: LogInterface = log.with_name("Reminders", "ViewRemindersCommand")
        self.__reminder_manager: ReminderManagerInterface = reminder_manager
        self.group_name = "reminder"
        self.description = "Displays your reminders."
        self.components = [
            ComponentRegistration("reminder_paginator", Paginator, self.__on_page_changed, DeferType.DEFER_MESSAGE_UPDATE)
        ]

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        return CommandResponse(ReplyAction(
            await self.__create_page_content(context.author_id, 0, DEFAULT_PAGE_SIZE),
            Paginator("reminder_paginator", current_page=0)
        ))

    async def __on_page_changed(
        self,
        _registration: ComponentRegistration,
        context: InteractionContext,
        state: Any
    ) -> ComponentInteractionResponse:
        return ComponentInteractionResponse(
            EditMessageAction(
                await self.__create_page_content(
                    context.author_id,
                    max(state.current_page, 0),
                    DEFAULT_PAGE_SIZE
                ),
                Paginator("reminder_paginator", current_page=max(state.current_page, 0))
            )
            if isinstance(state, PagerState)
            else EditMessageAction("An internal error occurred while processing the interaction.")
        )

    async def __create_page_content(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> Union[str, Embed]:
        self.__log.trace(f"User requested to-do list page. {{ UserId = {user_id}, Page = {page_index} }}")
        start_offset = page_index * page_size
        reminders = await self.__reminder_manager.get_by_user(user_id, start_offset, page_size)
        if len(reminders) == 0:
            return "The user has no reminders."
        
        embed = Embed(
            title="Reminders",
            description=f"Reminders of {user_id}.",
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
