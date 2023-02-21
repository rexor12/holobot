from datetime import datetime
from typing import Any

from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import PagerState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.enums import RankingType
from holobot.extensions.general.managers import IMarriageManager
from holobot.extensions.general.models import GeneralOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

@injectable(IWorkflow)
class ViewMarriageRankingWorkflow(WorkflowBase):
    _DEFAULT_PAGE_SIZE = 10
    _RANKING_TYPE_KEY = "rt"

    def __init__(
        self,
        i18n_provider: II18nProvider,
        marriage_manager: IMarriageManager,
        options: IOptions[GeneralOptions]
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__marriage_manager = marriage_manager
        self.__options = options

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
        component_type=Paginator,
        is_bound=True
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: Any
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or not isinstance(state, PagerState)
        ):
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
        server_id: str,
        user_id: str,
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


        users = list[str]()
        levels = list[str]()
        married_ats = list[datetime]()
        for index, item in enumerate(result.items):
            rank = index + result.page_index * result.page_size + 1
            match len(users):
                case 0 if result.page_index == 0:
                    users.append(f"{rank}. {self.__options.value.RankingGoldTrophyEmoji} <@{item.user_id1}> x <@{item.user_id2}>")
                case 1 if result.page_index == 0:
                    users.append(f"{rank}. {self.__options.value.RankingSilverTrophyEmoji} <@{item.user_id1}> x <@{item.user_id2}>")
                case 2 if result.page_index == 0:
                    users.append(f"{rank}. {self.__options.value.RankingBronzeTrophyEmoji} <@{item.user_id1}> x <@{item.user_id2}>")
                case _:
                    users.append(f"{rank}. <@{item.user_id1}> x <@{item.user_id2}>")

            levels.append(str(item.level))
            married_ats.append(item.married_at)

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
                    )
                }
            ),
            fields=[
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.general.view_marriage_ranking_workflow.embed_users_name"
                    ),
                    value="\n".join(users)
                ),
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.general.view_marriage_ranking_workflow.embed_level_name"
                    ),
                    value="\n".join(levels)
                ),
                EmbedField(
                    name=self.__i18n_provider.get(
                        "extensions.general.view_marriage_ranking_workflow.embed_age_name"
                    ),
                    value="\n".join(
                        map(
                            lambda married_at: self.__i18n_provider.get(
                                "extensions.general.view_marriage_ranking_workflow.embed_age_format",
                                { "married_at" : int(married_at.timestamp()) }
                            ),
                            married_ats
                        )
                    )
                )
            ]
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
