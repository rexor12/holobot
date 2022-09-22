from typing import Any

from holobot.discord.sdk.actions import EditMessageAction, ReplyAction
from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComboBox, ComboBoxItem, ComponentBase, LayoutBase, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.models import ComboBoxState, PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import EntityType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.extensions.giveaways.repositories import IExternalGiveawayItemRepository
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import try_parse_int

_ITEMS_PER_PAGE: int = 5

@injectable(IWorkflow)
class ViewActiveGiveawaysWorkflow(WorkflowBase):
    def __init__(
        self,
        external_giveaway_item_repository: IExternalGiveawayItemRepository,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__repository = external_giveaway_item_repository

    @command(
        description="Displays the currently available giveaways.",
        name="view",
        group_name="giveaway",
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        cooldown=Cooldown(duration=10, entity_type=EntityType.CHANNEL)
    )
    async def show_giveaways(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        content, layout = await self.__create_page_content(
            0,
            _ITEMS_PER_PAGE,
            "game",
            0,
            context.author_id
        )
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
            return InteractionResponse(EditMessageAction(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            ))

        identifier, page_index, item_index, item_type = state.selected_values[0].split(";")
        if (not identifier
            or not item_type
            or (page_index := try_parse_int(page_index)) is None
            or (item_index := try_parse_int(item_index)) is None):
            return InteractionResponse(EditMessageAction(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            ))

        content, components = await self.__create_page_content(
            page_index,
            _ITEMS_PER_PAGE,
            item_type,
            item_index,
            context.author_id
        )
        return InteractionResponse(
            EditMessageAction(
                content=content,
                components=components
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
            return InteractionResponse(EditMessageAction(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            ))

        content, components = await self.__create_page_content(
            state.current_page,
            _ITEMS_PER_PAGE,
            state.custom_data.get("item_type", "game") or "game",
            0,
            context.author_id
        )
        return InteractionResponse(
            EditMessageAction(
                content=content,
                components=components
            )
        )

    async def __create_page_content(
        self,
        page_index: int,
        page_size: int,
        item_type: str,
        item_index: int,
        initiator_id: str
    ) -> tuple[str | Embed, ComponentBase | list[LayoutBase]]:
        metadatas = await self.__repository.get_metadatas(page_index, page_size, item_type)
        if page_index > 0 and not metadatas.items:
            page_index = 0
            item_index = 0
            metadatas = await self.__repository.get_metadatas(page_index, page_size, item_type)

        if not metadatas.items:
            return (
                self.__i18n_provider.get(
                    "extensions.giveaways.view_active_giveaways_workflow.no_active_giveaways"
                ),
                []
            )

        if item_index >= len(metadatas.items):
            item_index = 0

        return (
            await self.__create_embed(metadatas.items[item_index].identifier),
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
                            for index, item in enumerate(metadatas.items)
                        ],
                        placeholder=self.__i18n_provider.get(
                            "extensions.giveaways.view_active_giveaways_workflow.selector_placeholder"
                        )
                    )
                ]),
                Paginator(
                    id="gabpagi",
                    owner_id=initiator_id,
                    current_page=page_index,
                    page_size=page_size,
                    total_count=metadatas.total_count,
                    custom_data={
                        item_type: item_type
                    }
                )
            ]
        )

    async def __create_embed(self, item_id: int) -> Embed:
        item = await self.__repository.get(item_id)
        if not item:
            raise ArgumentError(
                "item_id",
                f"Cannot find the external giveaway item with identifier '{item_id}'."
            )

        return Embed(
            self.__i18n_provider.get(
                "extensions.giveaways.view_active_giveaways_workflow.embed_title"
            ),
            item.title,
            image_url=item.preview_url,
            fields=[
                EmbedField(
                    self.__i18n_provider.get(
                        "extensions.giveaways.view_active_giveaways_workflow.embed_field_expires"
                    ),
                    self.__i18n_provider.get(
                        "extensions.giveaways.view_active_giveaways_workflow.embed_field_expires_value",
                        { "end_time": int(item.end_time.timestamp()) }
                    )
                ),
                EmbedField(
                    self.__i18n_provider.get(
                        "extensions.giveaways.view_active_giveaways_workflow.embed_field_type"
                    ),
                    self.__i18n_provider.get(
                        f"extensions.giveaways.giveaway_types.{item.item_type}"
                    )
                ),
                EmbedField(
                    self.__i18n_provider.get(
                        "extensions.giveaways.view_active_giveaways_workflow.embed_field_claim_at"
                    ),
                    item.url,
                    False
                )
            ],
            footer=EmbedFooter(
                self.__i18n_provider.get(
                    "extensions.giveaways.view_active_giveaways_workflow.embed_footer",
                    { "source_name": item.source_name }
                )
            )
        )
