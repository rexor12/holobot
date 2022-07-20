from .. import AlertManagerInterface
from ..enums import PriceDirection
from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Paginator
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Any, Union

DEFAULT_PAGE_SIZE = 5

@injectable(IWorkflow)
class ViewAlarmsWorkflow(WorkflowBase):
    def __init__(self, alert_manager: AlertManagerInterface, log: LogInterface) -> None:
        super().__init__()
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.__log: LogInterface = log.with_name("Crypto", "ViewAlarmsWorkflow")

    @command(
        description="Displays your currently set alarms.",
        name="view",
        group_name="crypto",
        subgroup_name="alarm"
    )
    async def view_alarms(self, context: ServerChatInteractionContext) -> InteractionResponse:
        return InteractionResponse(ReplyAction(
            await self.__create_page_content(context.author_id, 0, DEFAULT_PAGE_SIZE),
            Paginator("crypto_alarm_paginator", current_page=0)
        ))

    @component(
        identifier="crypto_alarm_paginator",
        component_type=Paginator,
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
                Paginator("crypto_alarm_paginator", current_page=max(state.current_page, 0))
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
        self.__log.trace(f"User requested crypto alarm page. {{ UserId = {user_id}, Page = {page_index} }}")
        start_offset = page_index * page_size
        alerts = await self.__alert_manager.get_many(user_id, start_offset, page_size)
        if len(alerts) == 0:
            return "The user has no crypto alarms."
        
        embed = Embed(
            title="Crypto alarms",
            description=f"Cryptocurrency alarms of <@{user_id}>."
        )
        for alert in alerts:
            arrow = "🔼" if alert.direction == PriceDirection.ABOVE else "🔽"
            embed.fields.append(EmbedField(
                name=alert.symbol,
                value=f"{arrow} {alert.price:,.8f}",
                is_inline=False
            ))
        return embed
