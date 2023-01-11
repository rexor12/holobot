from typing import Any

from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import ButtonState, PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.reminders import IReminderManager
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewRemindersWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        reminder_manager: IReminderManager
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__logger = logger_factory.create(ViewRemindersWorkflow)
        self.__reminder_manager = reminder_manager

    @command(
        description="Displays your reminders.",
        name="view",
        group_name="reminder",
        cooldown=Cooldown(duration=10)
    )
    async def view_reminders(
        self,
        context: ServerChatInteractionContext
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
        identifier="reminder_viewall",
        component_type=Button,
        is_bound=True
    )
    async def view_reminders_by_button(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, ButtonState):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        content, embed, components = await self.__create_page_content(
            context.author_id,
            0,
            DEFAULT_PAGE_SIZE
        )
        return self._edit_message(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

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
        content, embed, components = await self.__create_page_content(
            state.owner_id,
            max(state.current_page, 0),
            DEFAULT_PAGE_SIZE
        )

        return (self._edit_message(
                content=content,
                embed=embed,
                components=components
            )
            if isinstance(state, PagerState)
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
        result = await self.__reminder_manager.get_by_user(user_id, page_index, page_size)
        if not result.items:
            return (
                self.__i18n_provider.get(
                    "extensions.reminders.view_reminders_workflow.no_reminders"
                ),
                None,
                None
            )

        embed = Embed(
            title=self.__i18n_provider.get(
                "extensions.reminders.view_reminders_workflow.embed_title"
            ),
            description=self.__i18n_provider.get(
                "extensions.reminders.view_reminders_workflow.embed_description",
                { "user_id": user_id }
            ),
            footer=EmbedFooter(
                self.__i18n_provider.get(
                    "extensions.reminders.view_reminders_workflow.embed_footer"
                )
            )
        )
        for reminder in result.items:
            embed.fields.append(EmbedField(
                name=self.__i18n_provider.get(
                    "extensions.reminders.view_reminders_workflow.embed_field_name",
                    { "reminder_id": reminder.identifier }
                ),
                value=self.__i18n_provider.get(
                    "extensions.reminders.view_reminders_workflow.embed_field_value",
                    {
                        "message": reminder.message or "???",
                        "time": int(reminder.next_trigger.timestamp()),
                        "repeats": (
                            ":white_check_mark:"
                            if reminder.is_repeating
                            else ":no_entry_sign:"
                        )
                    }
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

        return (None, embed, component)
