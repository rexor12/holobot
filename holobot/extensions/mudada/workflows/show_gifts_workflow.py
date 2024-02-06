from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.exceptions import ServerNotFoundError, UserNotFoundError
from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    ComponentBase, LayoutBase, Paginator
)
from holobot.discord.sdk.workflows.interactables.components.models import PaginatorState
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import (
    MUDADA_SERVER_ID, VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME
)
from holobot.extensions.mudada.repositories import ITransactionRepository
from holobot.extensions.mudada.workflows.decorators import requires_event
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

_PAGE_SIZE = 5

@injectable(IWorkflow)
class ShowGiftsWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        member_data_provider: IMemberDataProvider,
        transaction_repository: ITransactionRepository
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__transaction_repository = transaction_repository

    @requires_event(VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME)
    @command(
        group_name="mudada",
        name="gifts",
        description="Displays the list of gifts you have prepared so far.",
        server_ids={MUDADA_SERVER_ID},
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        cooldown=Cooldown(duration=10),
        is_ephemeral=True
    )
    async def show_gifts(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        content, embed, components = await self.__create_page_content(
            context.server_id,
            context.author_id,
            0,
            _PAGE_SIZE,
            context.author_id
        )

        return self._reply(
            content=content if isinstance(content, str) else None,
            embed=embed if isinstance(embed, Embed) else None,
            components=components
        )

    @requires_event(VALENTINES_2024_EVENT_TOGGLE_FEATURE_NAME)
    @component(
        identifier="mdd_resv_pagi",
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
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

        content, embed, components = await self.__create_page_content(
            context.server_id,
            state.owner_id,
            max(state.current_page, 0),
            _PAGE_SIZE,
            state.owner_id
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
        page_index: int,
        page_size: int,
        owner_id: str
    ) -> tuple[
        UndefinedOrNoneOr[str],
        UndefinedOrNoneOr[Embed],
        ComponentBase | list[LayoutBase] | None
    ]:
        result = await self.__transaction_repository.paginate_by_owner(user_id, page_index, page_size)
        if not result.items and result.total_count > 0:
            result = await self.__transaction_repository.paginate_by_owner(user_id, 0, page_size)

        if not result.items:
            return (
                self.__i18n.get("extensions.mudada.show_reservations_workflow.no_reservations_error"),
                None,
                None
            )

        embed_fields = list[EmbedField]()
        for item in result.items:
            embed_fields.append(EmbedField(
                name=await self.__get_user_display_name(server_id, item.target_id),
                value=self.__i18n.get(
                    "extensions.mudada.show_reservations_workflow.embed_item_with_message"
                    if item.message
                    else "extensions.mudada.show_reservations_workflow.embed_item",
                    {
                        "amount": item.amount,
                        "message": item.message
                    }
                ),
                is_inline=False
            ))

        embed = Embed(
            title=self.__i18n.get("extensions.mudada.show_reservations_workflow.embed_title"),
            description=self.__i18n.get("extensions.mudada.show_reservations_workflow.embed_description"),
            fields=embed_fields
        )

        component = Paginator(
            id="mdd_resv_pagi",
            owner_id=owner_id,
            current_page=result.page_index,
            page_size=result.page_size,
            total_count=result.total_count
        )

        return (None, embed, component)

    async def __get_user_display_name(
        self,
        server_id: str,
        user_id: str
    ) -> str:
        try:
            user_data = await self.__member_data_provider.get_basic_data_by_id(
                server_id,
                user_id
            )

            return user_data.display_name or user_id
        except (ServerNotFoundError, UserNotFoundError):
            return user_id
