from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils.string_utils import escape_user_text
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComboBox, ComboBoxItem, ComboBoxState, LayoutBase, Paginator, PaginatorState, StackLayout
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import MUDADA_FEATURE_NAME
from holobot.extensions.mudada.factories import ChartData, IRatingChartFactory
from holobot.extensions.mudada.models import Valentine2025Rating, Valentine2025RatingId
from holobot.extensions.mudada.repositories.valentine2025 import IValentine2025RatingRepository
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.string_utils import try_parse_int
from .helpers import color_to_hex, get_user_name_with_color, get_user_name_with_hex_color

_PAGE_SIZE: int = 5

@injectable(IWorkflow)
class ViewRatingWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        rating_chart_factory: IRatingChartFactory,
        rating_repository: IValentine2025RatingRepository
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__rating_chart_factory = rating_chart_factory
        self.__rating_repository = rating_repository

    @command(
        group_name="mudada",
        subgroup_name="valentine",
        name="mychart",
        description="See an aggregated chart of other users' ratings of you.",
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),)
    )
    async def view_my_chart(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error")
            )

        rating = await self.__rating_repository.get_aggregated_data(context.author_id)
        if not rating:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.mudada.view_rating_workflow.no_ratings_yet_error"
                )
            )

        user_name, user_color = await get_user_name_with_hex_color(
            self.__member_data_provider,
            context.server_id,
            context.author_id
        )
        chart_url = self.__rating_chart_factory.get_chart_url(
            user_name[:15],
            user_color,
            ChartData(
                score1=rating.average_score1,
                score2=rating.average_score2,
                score3=rating.average_score3,
                score4=rating.average_score4,
                score5=rating.average_score5,
                score6=rating.average_score6
            )
        )

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.view_rating_workflow.rating_chart",
                {
                    "chart_url": chart_url
                }
            )
        )

    @command(
        group_name="mudada",
        subgroup_name="valentine",
        name="myratings",
        description="See a list of all ratings you got from others.",
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),)
    )
    async def view_my_ratings(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n.get("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__create_ratings_view(
            context.server_id,
            None,
            context.author_id,
            0
        )

        return self._reply(
            content=content,
            embed=embed,
            components=components,
            is_ephemeral=True
        )

    @component(
        identifier="mv25sel",
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),)
    )
    async def display_rating(
        self,
        context: InteractionContext,
        state: ComboBoxState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n.get("interactions.server_only_interaction_error"),
                embed=None,
                components=None
            )

        source_user_id, page_index = state.selected_values[0].split("-")
        if (
            not source_user_id
            or not page_index
            or (source_user_id := try_parse_int(source_user_id)) is None
            or (page_index := try_parse_int(page_index)) is None
        ):
            return self._edit_message(
                content=self.__i18n.get("interactions.invalid_interaction_data_error"),
                embed=None,
                components=None
            )

        content, embed, components = await self.__create_ratings_view(
            context.server_id,
            source_user_id,
            context.author_id,
            page_index
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(
        identifier="mv25pag",
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),)
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n.get("interactions.server_only_interaction_error"),
                embed=None,
                components=None
            )

        content, embed, components = await self.__create_ratings_view(
            context.server_id,
            None,
            context.author_id,
            state.current_page
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    async def __create_ratings_view(
        self,
        server_id: int,
        source_user_id: int | None,
        target_user_id: int,
        page_index: int
    ) -> tuple[str | None, Embed | None, list[LayoutBase] | None]:
        metadatas = await self.__rating_repository.paginate_ratings(
            target_user_id,
            page_index,
            _PAGE_SIZE
        )
        if not metadatas.items and page_index > 0:
            page_index = 0
            metadatas = await self.__rating_repository.paginate_ratings(
                target_user_id,
                0,
                _PAGE_SIZE
            )

        if not metadatas.items:
            return (
                self.__i18n.get("extensions.mudada.view_rating_workflow.no_ratings_yet_error"),
                None,
                None
            )

        rating_id = Valentine2025RatingId(
            source_user_id=source_user_id if source_user_id else metadatas.items[0].source_user_id,
            target_user_id=target_user_id
        )
        rating = await self.__rating_repository.get(rating_id)
        if not rating:
            return (
                self.__i18n.get("extensions.mudada.view_rating_workflow.rating_not_found_error"),
                None,
                None
            )

        return (
            None,
            await self.__create_embed(rating, server_id),
            [
                StackLayout(
                    id="combo_box_container",
                    children=[
                        ComboBox(
                            id="mv25sel",
                            owner_id=target_user_id,
                            items=[
                                await self.__create_combo_box_item(
                                    page_index,
                                    server_id,
                                    item.source_user_id
                                )
                                for item in metadatas.items
                            ],
                            placeholder=self.__i18n.get(
                                "extensions.mudada.view_rating_workflow.combo_box_placeholder"
                            )
                        )
                    ]
                ),
                Paginator(
                    id="mv25pag",
                    owner_id=target_user_id,
                    current_page=page_index,
                    page_size=_PAGE_SIZE,
                    total_count=metadatas.total_count
                )
            ]
        )

    async def __create_combo_box_item(
        self,
        page_index: int,
        server_id: int,
        user_id: int
    ) -> ComboBoxItem:
        user_name, _ = await get_user_name_with_color(
            self.__member_data_provider,
            server_id,
            user_id
        )

        return ComboBoxItem(
            text=user_name,
            value=f"{user_id}-{page_index}"
        )

    async def __create_embed(
        self,
        rating: Valentine2025Rating,
        server_id: int
    ) -> Embed:
        source_name, color = await get_user_name_with_color(
            self.__member_data_provider,
            server_id,
            rating.identifier.source_user_id
        )
        target_name, _ = await get_user_name_with_hex_color(
            self.__member_data_provider,
            server_id,
            rating.identifier.target_user_id
        )

        return Embed(
            title=self.__i18n.get("extensions.mudada.view_rating_workflow.embed_title"),
            description=self.__i18n.get(
                "extensions.mudada.view_rating_workflow.embed_description_with_message"
                if rating.message
                else "extensions.mudada.view_rating_workflow.embed_description",
                {
                    "source_name": escape_user_text(source_name),
                    "message": escape_user_text(rating.message) if rating.message else None
                }
            ),
            color=color,
            image_url=self.__rating_chart_factory.get_chart_url(
                target_name[:15],
                color_to_hex(color),
                ChartData(
                    score1=rating.score1,
                    score2=rating.score2,
                    score3=rating.score3,
                    score4=rating.score4,
                    score5=rating.score5,
                    score6=rating.score6
                )
            )
        )
