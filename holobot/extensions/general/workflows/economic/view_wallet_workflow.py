from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, LayoutBase, Paginator, PaginatorState
)
from holobot.discord.sdk.workflows.interactables.components.component_utils import get_custom_int
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.options import EconomicOptions
from holobot.extensions.general.repositories import IUserItemRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

_PAGE_SIZE: int = 10

@injectable(IWorkflow)
class ViewWalletWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        options: IOptions[EconomicOptions],
        user_item_repository: IUserItemRepository
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__options = options
        self.__user_item_repository = user_item_repository

    @command(
        group_name="economic",
        name="wallet",
        description="Displays how much of each currency you own.",
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        cooldown=Cooldown(duration=10)
    )
    async def view_wallet(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        server_id = context.server_id if isinstance(context, ServerChatInteractionContext) else 0
        content, embed, components = await self.__create_page_content(
            context.author_id,
            server_id,
            True,
            0,
            _PAGE_SIZE
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @component(
        identifier="gn_wallet_pagi",
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def change_page(
        self,
        context: InteractionContext,
        state: PaginatorState
    ) -> InteractionResponse:
        if (
            not isinstance(context, ServerChatInteractionContext)
            or (user_id := get_custom_int(state.custom_data, "u", 0)) is None
        ):
            return self._edit_message(content=self.__i18n.get("interactions.invalid_interaction_data_error"))

        content, embed, components = await self.__create_page_content(
            user_id,
            get_custom_int(state.custom_data, "s", 0) or 0,
            state.custom_data.get("g", "0") == "1",
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
        user_id: int,
        server_id: int,
        include_global: bool,
        page_index: int,
        page_size: int
    ) -> tuple[
        UndefinedOrNoneOr[str],
        UndefinedOrNoneOr[Embed],
        ComponentBase | list[LayoutBase] | None
    ]:
        result = await self.__user_item_repository.paginate_wallets_with_details(
            user_id,
            server_id,
            include_global,
            page_index,
            page_size
        )
        if not result.items and result.total_count > 0:
            result = await self.__user_item_repository.paginate_wallets_with_details(
                user_id,
                server_id,
                include_global,
                0,
                page_size
            )

        if not result.items:
            return (
                self.__i18n.get("extensions.general.view_wallet_workflow.empty_wallet_error"),
                None,
                None
            )

        currency_descriptions = self.__i18n.get_list_items(
            "extensions.general.view_wallet_workflow.currency_description",
            ({
                "amount": wallet.amount,
                "emoji_name": wallet.currency_emoji_name,
                "emoji_id": wallet.currency_emoji_id
            }
            for wallet in result.items)
        )

        embed = Embed(
            title=self.__i18n.get("extensions.general.view_wallet_workflow.embed_title"),
            description=self.__i18n.get(
                "extensions.general.view_wallet_workflow.wallet_description",
                {
                    "currencies": "\n".join(currency_descriptions)
                }
            ),
            thumbnail_url=self.__options.value.WalletEmbedThumbnailUrl
        )

        layouts = Paginator(
            id="gn_wallet_pagi",
            owner_id=user_id,
            current_page=result.page_index,
            page_size=result.page_size,
            total_count=result.total_count,
            custom_data={
                "u": user_id,
                "s": server_id,
                "g": "1" if include_global else "0"
            }
        )

        return (None, embed, layouts)
