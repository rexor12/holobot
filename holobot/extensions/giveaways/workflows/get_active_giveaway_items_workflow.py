from typing import Any, Dict, List, Tuple, Union

from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComboBox, ComboBoxItem, ComponentBase, Layout, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.enums import ComponentStyle
from holobot.discord.sdk.workflows.interactables.components.models import ComboBoxState, PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.extensions.giveaways.repositories import IExternalGiveawayItemRepository
from holobot.extensions.giveaways.models import ExternalGiveawayItem
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils import try_parse_int

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
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def show_giveaways(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        content, layout = await self.__create_page_content(0, ITEMS_PER_PAGE, "game", 0, context.author_id)
        return InteractionResponse(
            action=ReplyAction(content=content, components=layout)
        )

    @component(
        identifier="giveaway_selector",
        component_type=ComboBox,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def display_giveaway(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, ComboBoxState):
            return InteractionResponse(EditMessageAction((
                "This interaction isn't valid anymore. If this problem persists,"
                " please report the issue (see `/info`)."
            )))

        if len(state.selected_values) != 1:
            return InteractionResponse(EditMessageAction("You must select a single giveaway."))

        identifier, page_index, item_index, item_type = state.selected_values[0].split(";")
        if (not identifier
            or not item_type
            or (page_index := try_parse_int(page_index)) is None
            or (item_index := try_parse_int(item_index)) is None):
            return InteractionResponse(EditMessageAction((
                "This interaction isn't valid anymore. If this problem persists,"
                " please report the issue (see `/info`)."
            )))

        return InteractionResponse(
            EditMessageAction(
                *await self.__create_page_content(
                    page_index,
                    ITEMS_PER_PAGE,
                    item_type,
                    item_index,
                    context.author_id
                )
            )
        )

    @component(
        identifier="gabpagi",
        component_type=Paginator
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if not isinstance(state, PagerState):
            return InteractionResponse(EditMessageAction((
                "This interaction isn't valid anymore. If this problem persists,"
                " please report the issue (see `/info`)."
            )))

        if not (item_type := state.custom_data.get("item_type", "game")):
            return InteractionResponse(EditMessageAction((
                "This interaction isn't valid anymore. If this problem persists,"
                " please report the issue (see `/info`)."
            )))

        return InteractionResponse(
            EditMessageAction(
                *await self.__create_page_content(
                    state.current_page,
                    ITEMS_PER_PAGE,
                    item_type,
                    0,
                    context.author_id
                )
            )
        )

    async def __create_page_content(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        item_index: int,
        initiator_id: str
    ) -> Tuple[Union[str, Embed], Union[ComponentBase, List[Layout]]]:
        result = await self.__repository.get_many(page_index, page_size, item_type)
        if page_index > 0 and len(result.items) == 0:
            page_index = 0
            item_index = 0
            result = await self.__repository.get_many(page_index, page_size, item_type)

        if len(result.items) == 0:
            return ("Currently, there are no active giveaways. Check back later.", [])

        if item_index >= len(result.items):
            item_index = 0

        content = GetActiveGiveawayItemsWorkflow.__create_embed(result.items[item_index])
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
                            for index, item in enumerate(result.items)
                        ],
                        placeholder="Choose a giveaway"
                    )
                ]),
                Paginator(
                    id="gabpagi",
                    owner_id=initiator_id,
                    current_page=page_index,
                    page_size=page_size,
                    total_count=result.total_count,
                    custom_data={
                        item_type: item_type
                    }
                )
            ]
        )

    @staticmethod
    def __create_embed(item: ExternalGiveawayItem) -> Embed:
        return Embed(
            "Giveaway details",
            item.title,
            image_url=item.preview_url,
            fields=[
                EmbedField("Expires", f"<t:{int(item.end_time.timestamp())}:R>"),
                EmbedField("Type", ITEM_TYPE_I18N[item.item_type] if item.item_type in ITEM_TYPE_I18N else item.item_type),
                EmbedField("Claim at", item.url, False)
            ],
            footer=EmbedFooter(f"Sponsored by {item.source_name}")
        )
