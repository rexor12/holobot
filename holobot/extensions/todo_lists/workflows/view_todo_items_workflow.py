from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import (
    ButtonState, PaginatorState
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr
from .. import ITodoItemManager

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewTodoItemsWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        todo_item_manager: ITodoItemManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(ViewTodoItemsWorkflow)
        self.__todo_item_manager = todo_item_manager

    @command(
        description="Displays all your to-do items.",
        name="view",
        group_name="todo",
        cooldown=Cooldown(duration=10)
    )
    async def view_todo_items(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        content, embed, components = await self.__create_page_content(
            context.author_id,
            0,
            DEFAULT_PAGE_SIZE
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @component(
        identifier="todo_viewall",
        is_bound=True
    )
    async def view_todo_items_by_button(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        content, embed, components = await self.__create_page_content(
            context.author_id,
            0,
            DEFAULT_PAGE_SIZE
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @component(
        identifier="todo_paginator",
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        content, embed, components = await self.__create_page_content(
            state.owner_id,
            max(state.current_page, 0),
            DEFAULT_PAGE_SIZE
        )

        return (
            self._edit_message(
                content=content,
                embed=embed,
                components=components
            )
            if isinstance(state, PaginatorState)
            else self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )
        )

    async def __create_page_content(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> tuple[
            UndefinedOrNoneOr[str],
            UndefinedOrNoneOr[Embed],
            ComponentBase | list[LayoutBase] | None
        ]:
        self.__logger.trace("User requested to-do list page", user_id=user_id, page_index=page_index)
        result = await self.__todo_item_manager.get_by_user(user_id, page_index, page_size)
        if not result.items:
            return (
                self.__i18n_provider.get(
                    "extensions.todo_lists.view_todo_items_workflow.no_todo_items"
                ),
                None,
                None
            )

        embed = Embed(
            title=self.__i18n_provider.get(
                "extensions.todo_lists.view_todo_items_workflow.embed_title"
            ),
            description=self.__i18n_provider.get(
                "extensions.todo_lists.view_todo_items_workflow.embed_description",
                { "user_id": user_id }
            ),
            fields=[
                EmbedField(
                    self.__i18n_provider.get(
                        "extensions.todo_lists.view_todo_items_workflow.embed_field",
                        { "item_id": item.identifier }
                    ),
                    item.message,
                    False
                )
                for item in result.items
            ],
            footer=EmbedFooter(self.__i18n_provider.get(
                "extensions.todo_lists.view_todo_items_workflow.embed_footer"
            ))
        )

        component = Paginator(
            id="todo_paginator",
            owner_id=user_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count
        )

        return (None, embed, component)
