from typing import Any, List, Tuple, Union

from .. import TodoItemManagerInterface
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
from holobot.sdk.logging import ILoggerFactory

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewTodoItemsWorkflow(WorkflowBase):
    def __init__(
        self,
        logger_factory: ILoggerFactory,
        todo_item_manager: TodoItemManagerInterface
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(ViewTodoItemsWorkflow)
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
            *await self.__create_page_content(
                context.author_id,
                0,
                DEFAULT_PAGE_SIZE
            )
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
        self.__logger.trace("User requested to-do list page", user_id=user_id, page_index=page_index)
        result = await self.__todo_item_manager.get_by_user(user_id, page_index, page_size)
        if len(result.items) == 0:
            return ("There are no to-do items on this page.", [])

        content = Embed(
            title="To-do list",
            description=f"To-do items of <@{user_id}>.",
            fields=[
                EmbedField(f"#{item.id}", item.message, False) for item in result.items
            ],
            footer=EmbedFooter("Use the to-do item's number for removal.")
        )

        component = Paginator(
            id="todo_paginator",
            owner_id=user_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count
        )
        
        return (content, component)
