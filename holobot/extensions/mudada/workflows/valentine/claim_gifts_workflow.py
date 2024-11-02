from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import (
    Button, ComponentBase, LayoutBase, Paginator, StackLayout
)
from holobot.discord.sdk.workflows.interactables.components.models import (
    ButtonState, PaginatorState
)
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import MUDADA_FEATURE_NAME
from holobot.extensions.mudada.models import Wallet
from holobot.extensions.mudada.repositories import ITransactionRepository, IWalletRepository
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils.type_utils import UndefinedOrNoneOr

_PAGE_SIZE: int = 5

@injectable(IWorkflow)
class ClaimGiftsWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        transaction_repository: ITransactionRepository,
        unit_of_work_provider: IUnitOfWorkProvider,
        wallet_repository: IWalletRepository
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__transaction_repository = transaction_repository
        self.__unit_of_work_provider = unit_of_work_provider
        self.__wallet_repository = wallet_repository

    @command(
        group_name="mudada",
        subgroup_name="valentine",
        name="claimgifts",
        description="View and claim your available gifts.",
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),),
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        cooldown=Cooldown(duration=10),
        is_ephemeral=True
    )
    async def claim_gifts(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        content, embed, components = await self.__create_page_content(
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

    @component(
        identifier="mdd_gcall",
        is_bound=True,
        defer_type=DeferType.DEFER_MESSAGE_UPDATE
    )
    async def claim_all_gifts(
        self,
        context: InteractionContext,
        state: ButtonState
    ) -> InteractionResponse:
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            # NOTE: owner_id can be used here since this callback is bound to the "target" user.
            transactions = await self.__transaction_repository.get_finalized_uncompleted_by_target(state.owner_id)
            if len(transactions) == 0:
                return self._edit_message(
                    content=self.__i18n.get("extensions.mudada.claim_gifts_workflow.no_gifts_error"),
                    embed=None
                )

            total_amount = sum(map(lambda i: i.amount, transactions))
            wallet = await self.__wallet_repository.get(state.owner_id)
            if wallet:
                wallet.amount += total_amount
                await self.__wallet_repository.update(wallet)
            else:
                wallet = Wallet(
                    identifier=state.owner_id,
                    amount=total_amount
                )
                await self.__wallet_repository.add(wallet)

            await self.__transaction_repository.complete_many(tuple(map(lambda i: i.identifier, transactions)))

            unit_of_work.complete()

        return self._edit_message(
            content=self.__i18n.get(
                "extensions.mudada.claim_gifts_workflow.successful_claim",
                {
                    "claim_amount": total_amount,
                    "wallet_amount": wallet.amount
                }
            ),
            embed=None
        )

    @component(
        identifier="mdd_claim_pagi",
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
        user_id: str,
        page_index: int,
        page_size: int,
        owner_id: str
    ) -> tuple[
        UndefinedOrNoneOr[str],
        UndefinedOrNoneOr[Embed],
        ComponentBase | list[LayoutBase] | None
    ]:
        result = await self.__transaction_repository.paginate_by_target(user_id, page_index, page_size, True)
        if not result.items and result.total_count > 0:
            result = await self.__transaction_repository.paginate_by_target(user_id, 0, page_size, True)

        if not result.items:
            return (
                self.__i18n.get("extensions.mudada.claim_gifts_workflow.no_gifts_error"),
                None,
                None
            )

        embed_description_items = list[str]()
        for index, item in enumerate(result.items):
            embed_description_items.append(self.__i18n.get(
                "extensions.mudada.claim_gifts_workflow.embed_description_gift"
                if not item.message
                else "extensions.mudada.claim_gifts_workflow.embed_description_gift_with_message",
                {
                    "index": index + 1,
                    "message": item.message,
                    "amount": item.amount
                }
            ))

        embed = Embed(
            title=self.__i18n.get("extensions.mudada.claim_gifts_workflow.embed_title"),
            description=self.__i18n.get(
                "extensions.mudada.claim_gifts_workflow.embed_description",
                {
                    "items": "\n\n".join(embed_description_items)
                }
            )
        )

        layouts = list[LayoutBase]()
        layouts.append(StackLayout(
            id="mdd_cball",
            children=[
                Button(
                    id="mdd_gcall",
                    owner_id=owner_id,
                    text=self.__i18n.get("extensions.mudada.claim_gifts_workflow.claim_all_button")
                )
            ]
        ))
        layouts.append(Paginator(
            id="mdd_claim_pagi",
            owner_id=owner_id,
            current_page=result.page_index,
            page_size=result.page_size,
            total_count=result.total_count
        ))

        return (None, embed, layouts)
