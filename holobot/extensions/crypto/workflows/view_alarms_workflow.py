from typing import Any

from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import ComponentBase, Layout, Paginator
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from .. import AlertManagerInterface
from ..enums import PriceDirection

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewAlarmsWorkflow(WorkflowBase):
    def __init__(
        self,
        alert_manager: AlertManagerInterface,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.__log = logger_factory.create(ViewAlarmsWorkflow)

    @command(
        description="Displays your currently set alarms.",
        name="view",
        group_name="crypto",
        subgroup_name="alarm"
    )
    async def view_alarms(self, context: ServerChatInteractionContext) -> InteractionResponse:
        content, components = await self.__create_page_content(
            context.author_id,
            0,
            DEFAULT_PAGE_SIZE
        )
        return InteractionResponse(ReplyAction(
            content=content,
            components=components
        ))

    @component(
        identifier="crya_paginator",
        component_type=Paginator,
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        content, components = await self.__create_page_content(
            state.owner_id,
            max(state.current_page, 0),
            DEFAULT_PAGE_SIZE
        )
        return InteractionResponse(
            EditMessageAction(
                content=content,
                components=components
            )
            if isinstance(state, PagerState)
            else EditMessageAction(content="An internal error occurred while processing the interaction.")
        )

    async def __create_page_content(
        self,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> tuple[str | Embed, ComponentBase | list[Layout]]:
        self.__log.trace("User requested crypto alarm page", user_id=user_id, page_index=page_index)
        result = await self.__alert_manager.get_many(user_id, page_index, page_size)
        if not result.items:
            return ("The user has no crypto alarms.", [])

        embed = Embed(
            title="Crypto alarms",
            description=f"Cryptocurrency alarms of <@{user_id}>."
        )
        for alert in result.items:
            arrow = "🔼" if alert.direction is PriceDirection.ABOVE else "🔽"
            embed.fields.append(EmbedField(
                name=alert.symbol,
                value=f"{arrow} {alert.price:,.8f}",
                is_inline=False
            ))

        component = Paginator(
            id="crya_paginator",
            owner_id=user_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count
        )

        return (embed, component)
