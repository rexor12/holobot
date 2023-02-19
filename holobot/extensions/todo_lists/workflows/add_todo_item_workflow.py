from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Button, StackLayout
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.extensions.todo_lists import ITodoItemManager
from holobot.extensions.todo_lists.exceptions import TooManyTodoItemsError
from holobot.extensions.todo_lists.models import TodoItem
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class AddTodoItemWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        todo_item_manager: ITodoItemManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__todo_item_manager = todo_item_manager

    @command(
        description="Adds a new item to your to-do list.",
        name="add",
        group_name="todo",
        options=(
            Option("description", "The description of the to-do item."),
        ),
        cooldown=Cooldown(duration=10)
    )
    async def add_todo_item(
        self,
        context: InteractionContext,
        description: str
    ) -> InteractionResponse:
        todo_item = TodoItem(
            user_id=context.author_id,
            message=description
        )
        try:
            await self.__todo_item_manager.add_todo_item(todo_item)
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.todo_lists.add_todo_item_workflow.item_added",
                    {
                        "todo_item_id": todo_item.identifier
                    }
                ),
                components=[
                    StackLayout(
                        id="add_todo_item_layout",
                        children=[
                            Button(
                                id="todo_viewall",
                                owner_id=context.author_id,
                                text=self.__i18n_provider.get("common.buttons.view_all"),
                                style=ComponentStyle.PRIMARY
                            ),
                            Button(
                                id="todo_cancel",
                                owner_id=context.author_id,
                                text=self.__i18n_provider.get("common.buttons.cancel"),
                                style=ComponentStyle.SECONDARY,
                                custom_data={
                                    "tid": str(todo_item.identifier)
                                }
                            )
                        ]
                    )
                ]
            )
        except ArgumentOutOfRangeError as error:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.todo_lists.add_todo_item_workflow.message_too_long_error",
                    {
                        "lower_bound": error.lower_bound,
                        "upper_bound": error.upper_bound
                    }
                )
            )
        except TooManyTodoItemsError:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.todo_lists.add_todo_item_workflow.list_full_error"
                )
            )
