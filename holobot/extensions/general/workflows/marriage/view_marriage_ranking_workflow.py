from typing import Any

from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import PaginatorState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.enums import RankingType
from holobot.extensions.general.managers import IMarriageManager
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.iterable_utils import select_many
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

@injectable(IWorkflow)
class ViewMarriageRankingWorkflow(WorkflowBase):
    _DEFAULT_PAGE_SIZE = 10
    _RANKING_TYPE_KEY = "rt"

    def __init__(
        self,
        i18n_provider: II18nProvider,
        marriage_manager: IMarriageManager,
        member_data_provider: IMemberDataProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__marriage_manager = marriage_manager
        self.__member_data_provider = member_data_provider

    @command(
        group_name="marriage",
        name="ranking",
        description="Shows the marriage rankings.",
        options=(
            Option("type", "The type of the rankings.", OptionType.INTEGER, False, choices=(
                Choice("Level", RankingType.LEVEL),
                Choice("Age", RankingType.AGE)
            )),
        ),
        cooldown=Cooldown(duration=15)
    )
    async def view_marriage_rankings(
        self,
        context: InteractionContext,
        type: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        content, embed, components = await self.__create_page_content(
            context.server_id,
            context.author_id,
            RankingType(type) if type is not None else RankingType.LEVEL,
            0,
            ViewMarriageRankingWorkflow._DEFAULT_PAGE_SIZE
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @component(
        identifier="marrirank_paginator",
        is_bound=True
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(
                content=self.__i18n_provider.get("interactions.invalid_interaction_data_error")
            )

        ranking_type = (
            RankingType(int(value))
            if (value := state.custom_data.get(ViewMarriageRankingWorkflow._RANKING_TYPE_KEY, None)) is not None
            else RankingType.LEVEL
        )
        content, embed, components = await self.__create_page_content(
            context.server_id,
            state.owner_id,
            ranking_type,
            max(state.current_page, 0),
            ViewMarriageRankingWorkflow._DEFAULT_PAGE_SIZE
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    async def __create_page_content(
        self,
        server_id: int,
        user_id: int,
        ranking_type: RankingType,
        page_index: int,
        page_size: int
    ) -> tuple[
            UndefinedOrNoneOr[str],
            UndefinedOrNoneOr[Embed],
            ComponentBase | list[LayoutBase] | None
        ]:
        result = await self.__marriage_manager.get_ranking_infos(
            server_id,
            ranking_type,
            page_index,
            page_size
        )
        if not result.items:
            return (
                self.__i18n_provider.get(
                    "extensions.general.view_marriage_ranking_workflow.no_married_users_error"
                ),
                None,
                None
            )


        users = list[Any]()
        user_datas = self.__member_data_provider.get_basic_data_by_ids(
            server_id,
            select_many(
                result.items,
                lambda i: (i.user_id1, i.user_id2)
            )
        )
        user_names = {
            user.user_id: user.display_name
            async for user in user_datas
        }
        i18n_key_prefix = (
            "extensions.general.view_marriage_ranking_workflow.age_"
            if ranking_type == RankingType.AGE
            else "extensions.general.view_marriage_ranking_workflow.level_"
        )
        for index, item in enumerate(result.items):
            rank = index + result.page_index * result.page_size + 1
            match rank:
                case 1:
                    i18n_key = f"{i18n_key_prefix}top1_descriptor"
                case 2:
                    i18n_key = f"{i18n_key_prefix}top2_descriptor"
                case 3:
                    i18n_key = f"{i18n_key_prefix}top3_descriptor"
                case _:
                    i18n_key = f"{i18n_key_prefix}other_descriptor"
            users.append(
                self.__i18n_provider.get(
                    i18n_key,
                    {
                        "user_name1": user_names.get(item.user_id1, item.user_id1),
                        "user_name2": user_names.get(item.user_id2, item.user_id2),
                        "rank": rank,
                        "level": item.level,
                        "married_at": int(item.married_at.timestamp())
                    }
                )
            )

        embed = Embed(
            title=self.__i18n_provider.get(
                "extensions.general.view_marriage_ranking_workflow.embed_title"
            ),
            description=self.__i18n_provider.get(
                "extensions.general.view_marriage_ranking_workflow.embed_description",
                {
                    "ranking_type": self.__i18n_provider.get_list_item(
                        "extensions.general.view_marriage_ranking_workflow.ranking_types",
                        ranking_type.value
                    ),
                    "rankings": "\n".join(users)
                }
            )
        )

        component = Paginator(
            id="marrirank_paginator",
            owner_id=user_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count,
            custom_data={ ViewMarriageRankingWorkflow._RANKING_TYPE_KEY: ranking_type }
        )

        return (None, embed, component)
