from datetime import datetime, timezone
from typing import Dict, List, Tuple, Union

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComboBox, ComboBoxItem, ComponentBase, Layout, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.extensions.giveaways.repositories import IExternalGiveawayItemRepository
from holobot.extensions.giveaways.models import ExternalGiveawayItem
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import textify_timedelta, try_parse_int

ITEMS_PER_PAGE: int = 5
ITEM_TYPE_I18N: Dict[str, str] = {
    "game": "Game"
}

@injectable(IWorkflow)
class GetActiveGiveawayItemsWorkflow(WorkflowBase):
    def __init__(
        self,
        external_giveaway_item_repository: IExternalGiveawayItemRepository,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(GetActiveGiveawayItemsWorkflow)
        self.__repository: IExternalGiveawayItemRepository = external_giveaway_item_repository

    @command(
        description="Displays the currently available giveaways.",
        name="view",
        group_name="giveaway",
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def show_giveaways(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        content, layout = await self.__create_page_content(0, ITEMS_PER_PAGE, "game", 0, context.author_id)
        return InteractionResponse(
            action=ReplyAction(content=content, components=layout)
        )

    async def __create_page_content(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        item_index: int,
        initiator_id: str
    ) -> Tuple[Union[str, Embed], Union[ComponentBase, List[Layout]]]:
        items = await self.__repository.get_many(page_index * ITEMS_PER_PAGE, ITEMS_PER_PAGE, item_type)
        if page_index > 0 and len(items) == 0:
            page_index = 0
            item_index = 0
            items = await self.__repository.get_many(page_index * ITEMS_PER_PAGE, ITEMS_PER_PAGE, item_type)

        if len(items) == 0:
            return ("Currently, there are no active giveaways. Check back later.", [])

        if item_index >= len(items):
            item_index = 0

        content = GetActiveGiveawayItemsWorkflow.__create_embed(items[item_index])
        return (
            content,
            [
                StackLayout(id="combo_box_container", children=[
                    ComboBox(
                        id="giveaway_selector",
                        owner_id=initiator_id,
                        items=[
                            ComboBoxItem(
                                text=item.title,
                                value=f"{item.identifier};{page_index};{index};{item_type}"
                            )
                            for index, item in enumerate(items)
                        ],
                        placeholder="Choose a giveaway"
                    )
                ]),
                Paginator(
                    id="gabpagi",
                    owner_id=initiator_id,
                    current_page=page_index,
                    page_size=page_size,
                    total_count=3, # TODO Paginating query.
                    custom_data={
                        item_type: item_type
                    }
                )
            ]
        )

    # async def __on_giveaway_selected(self, registration: ComponentRegistration, context: InteractionContext, state: ComboBoxState) -> ComponentInteractionResponse:
    #     if len(state.selected_values) != 1:
    #         return ComponentInteractionResponse(ReplyAction("You must select a single giveaway."))

    #     identifier, page_index, item_index, item_type = state.selected_values[0].split(";")
    #     if (not identifier
    #         or not item_type
    #         or (page_index := try_parse_int(page_index)) is None
    #         or (item_index := try_parse_int(item_index)) is None):
    #         return ComponentInteractionResponse(ReplyAction((
    #             "An error occurred while processing your request. If this appened while you were"
    #             " navigating the bot's components, please contact the developer."
    #         )))

    #     return ComponentInteractionResponse(await self.__create_response_action(page_index, item_index, item_type, False))

    # async def __on_show_previous(self, registration: ComponentRegistration, context: InteractionContext, state: ButtonState) -> ComponentInteractionResponse:
    #     return await self.__change_page(state.data)

    # async def __on_show_next(self, registration: ComponentRegistration, context: InteractionContext, state: ButtonState) -> ComponentInteractionResponse:
    #     return await self.__change_page(state.data)

    # async def __change_page(self, button_data: str) -> ComponentInteractionResponse:
    #     page_index, item_index, item_type = button_data.split(";")
    #     if (not item_type
    #         or (page_index := try_parse_int(page_index)) is None
    #         or (item_index := try_parse_int(item_index)) is None):
    #         self.__logger.error(f"Failed to change giveaway item page. {{ Data = {button_data} }}")
    #         return ComponentInteractionResponse(ReplyAction((
    #             "An error occurred while processing your request. If this appened while you were"
    #             " navigating the bot's components, please contact the developer."
    #         )))

    #     return ComponentInteractionResponse(await self.__create_response_action(page_index, item_index, item_type, False))

    @staticmethod
    def __create_embed(item: ExternalGiveawayItem) -> Embed:
        return Embed(
            "Giveaway details",
            item.title,
            image_url=item.preview_url,
            fields=[
                EmbedField("Expires in", textify_timedelta(item.end_time - datetime.now(timezone.utc), only_largest_remaining=True)),
                EmbedField("Type", ITEM_TYPE_I18N[item.item_type] if item.item_type in ITEM_TYPE_I18N else item.item_type),
                EmbedField("Claim at", item.url, False)
            ],
            footer=EmbedFooter(f"Sponsored by {item.source_name}")
        )
