from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import PaginatorState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.extensions.general.repositories.user_profiles import IUserProfileRepository
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

@injectable(IWorkflow)
class ViewReputationRankingWorkflow(WorkflowBase):
    _DEFAULT_PAGE_SIZE = 10

    def __init__(
        self,
        i18n_provider: II18nProvider,
        user_data_provider: IUserDataProvider,
        user_profile_repository: IUserProfileRepository
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__user_data_provider = user_data_provider
        self.__user_profile_repository = user_profile_repository

    @command(
        group_name="reputation",
        name="ranking",
        description="Displays the global reputation ranking.",
        cooldown=Cooldown(duration=5)
    )
    async def view_reputation_ranking(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        content, embed, components = await self.__create_page_content(
            context.author_id,
            0,
            ViewReputationRankingWorkflow._DEFAULT_PAGE_SIZE
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @component(
        identifier="reprankpagi",
        is_bound=True
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        content, embed, components = await self.__create_page_content(
            state.owner_id,
            max(state.current_page, 0),
            ViewReputationRankingWorkflow._DEFAULT_PAGE_SIZE
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    async def __create_page_content(
        self,
        user_id: int,
        page_index: int,
        page_size: int
    ) -> tuple[
            UndefinedOrNoneOr[str],
            UndefinedOrNoneOr[Embed],
            ComponentBase | list[LayoutBase] | None
        ]:
        result = await self.__user_profile_repository.paginate_rankings(
            page_index,
            page_size
        )
        if not result.items:
            return (
                self.__i18n.get(
                    "extensions.general.view_reputation_ranking_workflow.no_reputations_error"
                ),
                None,
                None
            )

        user_datas = self.__user_data_provider.get_user_data_by_ids(
            map(lambda i: i.user_id, result.items)
        )
        user_names = {
            user.user_id: user.name
            async for user in user_datas
        }

        entries = list[str]()
        for index, item in enumerate(result.items):
            rank_index = result.page_index * result.page_size + index + 1
            user_name = user_names[item.user_id]
            entries.append(
                self.__i18n.get(
                    "extensions.general.view_reputation_ranking_workflow.table_entry",
                    {
                        "rank": str(rank_index).rjust(5),
                        "user_name": (
                            user_name[:13] + "..."
                            if len(user_name) > 13
                            else user_name.rjust(16)
                        ),
                        "reputation_points": f"{item.reputation_points:,}".rjust(12)
                    }
                )
            )

        content = [
            self.__i18n.get("extensions.general.view_reputation_ranking_workflow.message"),
            "```r",
            self.__i18n.get("extensions.general.view_reputation_ranking_workflow.table_header"),
            *entries,
            self.__i18n.get("extensions.general.view_reputation_ranking_workflow.table_footer"),
            "```"
        ]

        component = Paginator(
            id="reprankpagi",
            owner_id=user_id,
            current_page=page_index,
            page_size=page_size,
            total_count=result.total_count
        )

        return ("\n".join(content), None, component)
