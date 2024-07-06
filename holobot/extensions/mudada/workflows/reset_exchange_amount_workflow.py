from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.configs import MudadaOptions
from holobot.extensions.mudada.constants import MUDADA_SERVER_ID
from holobot.extensions.mudada.models import ExchangeQuota
from holobot.extensions.mudada.repositories import IExchangeQuotaRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ResetExchangeAmountWorkflow(WorkflowBase):
    def __init__(
        self,
        exchange_quota_repository: IExchangeQuotaRepository,
        i18n_provider: II18nProvider,
        options: IOptions[MudadaOptions],
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__exchange_quota_repository = exchange_quota_repository
        self.__i18n = i18n_provider
        self.__options = options
        self.__unit_of_work_provider = unit_of_work_provider

    @command(
        group_name="mudada",
        subgroup_name="quota",
        name="reset",
        description="Resets a user's exchange quota.",
        server_ids={MUDADA_SERVER_ID},
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        cooldown=Cooldown(duration=10),
        required_permissions=Permission.ADMINISTRATOR,
        options=(
            Option("user", "The user for whom to set the exchange quota.", OptionType.USER),
            Option("remaining_amount", "The remaining amount the user can exchange, up to the configured quota.", OptionType.INTEGER, False),
        )
    )
    async def reset_exchange_amount(
        self,
        context: InteractionContext,
        user: int,
        remaining_amount: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        if remaining_amount is None:
            used_amount = 0
        elif remaining_amount < 0:
            used_amount = self.__options.value.ExchangeQuotaPerUser
        elif remaining_amount > self.__options.value.ExchangeQuotaPerUser:
            used_amount = 0
        else:
            used_amount = self.__options.value.ExchangeQuotaPerUser - remaining_amount

        user_id = str(user)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            exchange_quota = await self.__exchange_quota_repository.get(user_id)
            if exchange_quota:
                exchange_quota.amount = used_amount
                await self.__exchange_quota_repository.update(exchange_quota)
            else:
                await self.__exchange_quota_repository.add(ExchangeQuota(
                    identifier=user_id,
                    amount=used_amount,
                    exchanged_amount=0,
                    lost_amount=0
                ))

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.mudada.set_exchange_quota_workflow.exchange_quota_set",
                {
                    "user_id": user_id,
                    "remaining_amount": self.__options.value.ExchangeQuotaPerUser - used_amount,
                    "max_quota": self.__options.value.ExchangeQuotaPerUser
                }
            ),
            suppress_user_mentions=True
        )
