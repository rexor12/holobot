from .. import ReminderManagerInterface
from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import ComponentBase, Layout, Paginator
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Any, List, Tuple, Union

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewRemindersWorkflow(WorkflowBase):
    def __init__(self, log: LogInterface, reminder_manager: ReminderManagerInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Reminders", "ViewRemindersWorkflow")
        self.__reminder_manager: ReminderManagerInterface = reminder_manager

    @command(
        description="Displays your reminders.",
        name="view",
        group_name="reminder"
    )
    async def view_reminders(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        return InteractionResponse(ReplyAction(
            *await self.__create_page_content(context.author_id, 0, DEFAULT_PAGE_SIZE)
        ))

    @component(
        identifier="reminder_paginator",
        component_type=Paginator,
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        return InteractionResponse(
            EditMessageAction(
                *await self.__create_page_content(
                    state.owner_id,
                    max(state.current_page, 0),
                    DEFAULT_PAGE_SIZE
                )
            )
            if isinstance(state, PagerState)
            else EditMessageAction("An internal error occurred while processing the interaction.")
        )

    async def __create_page_content(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> Tuple[Union[str, Embed], Union[ComponentBase, List[Layout]]]:
        self.__log.trace(f"User requested to-do list page. {{ UserId = {user_id}, Page = {page_index} }}")
        result = await self.__reminder_manager.get_by_user(user_id, page_index, page_size)
        if len(result.items) == 0:
            return ("The user has no reminders.", [])

        embed = Embed(
            title="Reminders",
            description=f"Reminders of <@{user_id}>.",
            footer=EmbedFooter("Use the reminder's number for removal.")
        )
        for reminder in result.items:
            embed.fields.append(EmbedField(
                name=f"#{reminder.id}",
                value=(
                    f"> Message: {reminder.message}\n"
                    f"> Next trigger: {reminder.next_trigger:%I:%M:%S %p, %m/%d/%Y} UTC\n"
                    f"> Repeats: {'yes' if reminder.is_repeating else 'no'}"
                ),
                is_inline=False
            ))

        component = Paginator(
            id="reminder_paginator",
            owner_id=user_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count
        )

        return (embed, component)
