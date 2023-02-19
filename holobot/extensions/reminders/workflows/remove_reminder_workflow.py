from typing import Any

from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Button
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import ButtonState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.extensions.reminders import IReminderManager
from holobot.extensions.reminders.exceptions import InvalidReminderError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.string_utils import try_parse_int

@injectable(IWorkflow)
class RemoveReminderWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        reminder_manager: IReminderManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(RemoveReminderWorkflow)
        self.__reminder_manager = reminder_manager

    @command(
        description="Removes a reminder.",
        name="remove",
        group_name="reminder",
        options=(
            Option("id", "The identifier of the reminder.", OptionType.INTEGER),
        )
    )
    async def remove_reminder(
        self,
        context: InteractionContext,
        id: int
    ) -> InteractionResponse:
        try:
            await self.__reminder_manager.delete_reminder(context.author_id, id)
            self.__logger.debug("Deleted a reminder", user_id=context.author_id, reminder_id=id)
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.remove_reminder_workflow.reminder_deleted"
                ),
                components=self.__get_view_all_button(context.author_id)
            )
        except InvalidReminderError:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.reminders.remove_reminder_workflow.reminder_not_found_error"
                ),
                components=self.__get_view_all_button(context.author_id)
            )

    @component(
        identifier="reminder_cancel",
        component_type=Button,
        is_bound=True
    )
    async def remove_reminder_by_button(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, ButtonState):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        reminder_id = try_parse_int(state.custom_data.get("rid", "-1")) or 0
        if not reminder_id:
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        try:
            await self.__reminder_manager.delete_reminder(context.author_id, reminder_id)
            self.__logger.debug("Deleted a reminder", user_id=context.author_id, reminder_id=reminder_id)
            return self._edit_message(
                content=self.__i18n_provider.get("extensions.reminders.remove_reminder_workflow.reminder_deleted"),
                components=self.__get_view_all_button(context.author_id)
            )
        except InvalidReminderError:
            return self._edit_message(
                content=self.__i18n_provider.get("extensions.reminders.remove_reminder_workflow.reminder_not_found_error"),
                components=self.__get_view_all_button(context.author_id)
            )

    def __get_view_all_button(self, author_id: str) -> Button:
        return Button(
            id="reminder_viewall",
            owner_id=author_id,
            text=self.__i18n_provider.get("common.buttons.view_all"),
            style=ComponentStyle.PRIMARY
        )
