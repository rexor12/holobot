from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command, component
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.interactables.restrictions import FeatureRestriction
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.constants import MUDADA_FEATURE_NAME
from holobot.extensions.mudada.repositories import IWalletRepository
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory

@injectable(IWorkflow)
class AdminTakeGiftsWorkflow(WorkflowBase):
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
        name="takegifts",
        description="Takes the specified number of gifts from a single user or ALL users.",
        options=(
            Option("number", "The number of gifts you'd like to take.", OptionType.INTEGER),
            Option("user", "The user you'd like to take gifts from.", OptionType.USER, False)
        ),
        required_permissions=Permission.ADMINISTRATOR,
        restrictions=(FeatureRestriction(feature_name=MUDADA_FEATURE_NAME),),
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def admin_take_gifts(
        self,
        context: InteractionContext,
        number: int,
        user: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        if number < 1:
            return self._reply(
                content=self.__i18n.get("extensions.mudada.admin_take_gifts_workflow.too_few_gifts_error")
            )

        if user is None:
            await self.__wallet_repository.remove_from_all_users(number)
            return self._reply(
                content=self.__i18n.get(
                    "extensions.mudada.admin_take_gifts_workflow.successfully_removed_gifts_from_all"
                )
            )

        user_id = str(user)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            wallet = await self.__wallet_repository.get(user_id)
            if not wallet:
                return self._reply(
                    content=self.__i18n.get(
                        "extensions.mudada.admin_take_gifts_workflow.user_has_no_gifts_error",
                        {
                            "user_id": user_id
                        }
                    )
                )

            wallet.amount = max(wallet.amount - number, 0)
            await self.__wallet_repository.update(wallet)
            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.admin_take_gifts_workflow.successfully_removed_gifts",
                {
                    "user_id": wallet.identifier,
                    "amount": wallet.amount
                }
            ),
            suppress_user_mentions=True
        )
