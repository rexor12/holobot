from typing import Any, Union

from .. import TodoItemManagerInterface
from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Paginator
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewTodoItemsWorkflow(WorkflowBase):
    def __init__(self, log: LogInterface, todo_item_manager: TodoItemManagerInterface) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("TodoLists", "ViewTodoItemsWorkflow")
        self.__todo_item_manager: TodoItemManagerInterface = todo_item_manager

    @command(
        description="Displays all your to-do items.",
        name="view",
        group_name="todo"
    )
    async def view_todo_items(
        self,
        context: ServerChatInteractionContext
    ) -> InteractionResponse:
        return InteractionResponse(ReplyAction(
            await self.__create_page_content(context.author_id, 0, DEFAULT_PAGE_SIZE),
            Paginator("todo_paginator", current_page=0)
        ))

    @component(
        identifier="todo_paginator",
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
                await self.__create_page_content(
                    context.author_id,
                    max(state.current_page, 0),
                    DEFAULT_PAGE_SIZE
                ),
                Paginator("todo_paginator", current_page=max(state.current_page, 0))
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
        items = await self.__todo_item_manager.get_by_user(user_id, start_offset, page_size)
        if len(items) == 0:
            return "The user has no to-do items."

        return Embed(
            title="To-do list",
            description=f"To-do items of <@{user_id}>.",
            fields=[
                EmbedField(f"#{item.id}", item.message, False) for item in items
            ],
            footer=EmbedFooter("Use the to-do item's number for removal.")
        )
