from typing import Any

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Button
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import ButtonState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.extensions.todo_lists import ITodoItemManager
from holobot.extensions.todo_lists.exceptions import InvalidTodoItemError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.string_utils import try_parse_int

@injectable(IWorkflow)
class RemoveTodoItemWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        todo_item_manager: ITodoItemManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__todo_item_manager = todo_item_manager

    @command(
        description="Removes a to-do item from your list.",
        name="remove",
        group_name="todo",
        options=(
            Option("identifier", "The identifier of the to-do item.", OptionType.INTEGER),
        )
    )
    async def remove_todo_item(
        self,
        context: InteractionContext,
        identifier: int
    ) -> InteractionResponse:
        try:
            await self.__todo_item_manager.delete_by_user(context.author_id, identifier)
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.todo_lists.remove_todo_item_workflow.item_deleted"
                ),
                components=self.__get_view_all_button(context.author_id)
            )
        except InvalidTodoItemError:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.todo_lists.remove_todo_item_workflow.no_todo_item_error"
                ),
                components=self.__get_view_all_button(context.author_id)
            )

    @component(
        identifier="todo_cancel",
        component_type=Button,
        is_bound=True
    )
    async def remove_todo_item_by_button(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, ButtonState):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        todo_item_id = try_parse_int(state.custom_data.get("tid", "-1")) or 0
        if not todo_item_id:
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        try:
            await self.__todo_item_manager.delete_by_user(context.author_id, todo_item_id)
            return self._edit_message(
                content=self.__i18n_provider.get("extensions.todo_lists.remove_todo_item_workflow.item_deleted"),
                components=self.__get_view_all_button(context.author_id)
            )
        except InvalidTodoItemError:
            return self._edit_message(
                content=self.__i18n_provider.get("extensions.todo_lists.remove_todo_item_workflow.no_todo_item_error"),
                components=self.__get_view_all_button(context.author_id)
            )

    def __get_view_all_button(self, author_id: str) -> Button:
        return Button(
            id="todo_viewall",
            owner_id=author_id,
            text=self.__i18n_provider.get("common.buttons.view_all"),
            style=ComponentStyle.PRIMARY
        )
