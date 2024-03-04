from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComponentBase, LayoutBase, Paginator, PaginatorState, StackLayout
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.models import EconomicOptions
from holobot.extensions.general.repositories import ICurrencyRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

_PAGE_SIZE: int = 5

@injectable(IWorkflow)
class ViewCurrenciesWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        i18n_provider: II18nProvider,
        options: IOptions[EconomicOptions]
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__i18n = i18n_provider
        self.__options = options

    @command(
        group_name="economic",
        subgroup_name="currency",
        name="view",
        description="Displays the currencies specific to this server.",
        cooldown=Cooldown(duration=10),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def view_currencies(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        content, embed, components = await self.__create_page_content(
            context.author_id,
            context.server_id,
            0,
            _PAGE_SIZE
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @component(
        identifier="gn_currency_view",
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_to_first_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(content=self.__i18n.get("interactions.invalid_interaction_data_error"))

        content, embed, components = await self.__create_page_content(
            context.author_id,
            context.server_id,
            0,
            _PAGE_SIZE
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    @component(
        identifier="gn_currency_pagi",
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._edit_message(content=self.__i18n.get("interactions.invalid_interaction_data_error"))

        content, embed, components = await self.__create_page_content(
            context.author_id,
            context.server_id,
            max(state.current_page, 0),
            _PAGE_SIZE
        )

        return self._edit_message(
            content=content,
            embed=embed,
            components=components
        )

    async def __create_page_content(
        self,
        owner_id: str,
        server_id: str,
        page_index: int,
        page_size: int
    ) -> tuple[
        UndefinedOrNoneOr[str],
        UndefinedOrNoneOr[Embed],
        ComponentBase | list[LayoutBase] | None
    ]:
        result = await self.__currency_repository.paginate_by_server(server_id, page_index, page_size, False)
        if not result.items and result.total_count > 0:
            result = await self.__currency_repository.paginate_by_server(server_id, 0, page_size, False)

        if not result.items:
            return (
                self.__i18n.get("extensions.general.view_currencies_workflow.no_custom_currencies_error"),
                None,
                None
            )

        currency_descriptions = self.__i18n.get_list_items(
            "extensions.general.view_currencies_workflow.currency_detail",
            ({
                "index": index + 1,
                "name": currency.name,
                "description": currency.description,
                "emoji_name": currency.emoji_name,
                "emoji_id": currency.emoji_id
            }
            for index, currency in enumerate(result.items))
        )

        embed = Embed(
            title=self.__i18n.get("extensions.general.view_currencies_workflow.embed_title"),
            description=self.__i18n.get(
                "extensions.general.view_currencies_workflow.currencies_description",
                {
                    "currencies": "\n".join(currency_descriptions)
                }
            ),
            thumbnail_url=self.__options.value.CurrenciesEmbedThumbnailUrl
        )

        buttons = list[ComponentBase]()
        for index, currency in enumerate(result.items):
            buttons.append(Button(
                id=f"gn_currency_del",
                owner_id=owner_id,
                text=f"#{index + 1}",
                emoji="❌",
                custom_data={
                    "i": str(currency.identifier)
                }
            ))

        button_layout = StackLayout(
            id="dummy",
            children=buttons
        )
        paginator = Paginator(
            id="gn_currency_pagi",
            owner_id=owner_id,
            current_page=result.page_index,
            page_size=result.page_size,
            total_count=result.total_count
        )

        return (None, embed, list[LayoutBase]((button_layout, paginator)))
