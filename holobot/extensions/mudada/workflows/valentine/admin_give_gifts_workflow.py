from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import MUDADA_FEATURE_NAME
from holobot.extensions.mudada.models import Wallet
from holobot.extensions.mudada.repositories import IWalletRepository
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

_GIFT_COUNT_MAX: int = 1_000_000_000

@injectable(IWorkflow)
class AdminGiveGiftsWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        logger_factory: ILoggerFactory,
        unit_of_work_provider: IUnitOfWorkProvider,
        wallet_repository: IWalletRepository
    ) -> None:
        super().__init__()
        self.__i18n = i18n_provider
        self.__unit_of_work_provider = unit_of_work_provider
        self.__wallet_repository = wallet_repository

    @command(
        group_name="mudada",
        subgroup_name="admin",
        name="givegifts",
        description="Gives the specified number of gifts to a user of your choice.",
        options=(
            Option("user", "The user you'd like to give gifts to.", OptionType.USER),
            Option("number", "The number of gifts you'd like to give.", OptionType.INTEGER)
        ),
        required_permissions=Permission.ADMINISTRATOR,
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def admin_give_gifts(
        self,
        context: InteractionContext,
        user: int,
        number: int
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        if number > _GIFT_COUNT_MAX:
            return self._reply(
                content=self.__i18n.get("extensions.mudada.admin_give_gifts_workflow.too_many_gifts_error")
            )

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            wallet = await self.__wallet_repository.get(user)
            if wallet:
                wallet.amount += number
                await self.__wallet_repository.update(wallet)
            else:
                wallet = Wallet(
                    identifier=user,
                    amount=number
                )
                await self.__wallet_repository.add(wallet)

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.admin_give_gifts_workflow.successfully_added_gifts",
                {
                    "user_id": wallet.identifier,
                    "amount": wallet.amount
                }
            ),
            suppress_user_mentions=True
        )
