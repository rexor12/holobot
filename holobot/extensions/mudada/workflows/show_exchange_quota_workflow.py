from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.models import Embed, EmbedFooter, InteractionContext
from holobot.discord.sdk.servers.imember_data_provider import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.mudada.configs import MudadaOptions
from holobot.extensions.mudada.constants import MUDADA_SERVER_ID
from holobot.extensions.mudada.repositories import IExchangeQuotaRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ShowExchangeQuotaWorkflow(WorkflowBase):
    def __init__(
        self,
        exchange_quota_repository: IExchangeQuotaRepository,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        options: IOptions[MudadaOptions]
    ) -> None:
        super().__init__()
        self.__exchange_quota_repository = exchange_quota_repository
        self.__i18n = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__options = options

    @command(
        group_name="mudada",
        subgroup_name="quota",
        name="view",
        description="Displays your exchange quota.",
        server_ids={MUDADA_SERVER_ID},
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        cooldown=Cooldown(duration=5),
        options=(
            Option("user", "The user to view; otherwise, it's yourself.", OptionType.USER, False),
        )
    )
    async def show_exchange_quota(
        self,
        context: InteractionContext,
        user: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        user_id = str(user) if user else context.author_id
        exchange_quota = await self.__exchange_quota_repository.get(user_id)
        if exchange_quota:
            remaining_amount = max(0, self.__options.value.ExchangeQuotaPerUser - exchange_quota.amount)
            exchanged_amount = exchange_quota.exchanged_amount
            lost_amount = exchange_quota.lost_amount
        else:
            remaining_amount = self.__options.value.ExchangeQuotaPerUser
            exchanged_amount = 0
            lost_amount = 0

        member = await self.__member_data_provider.get_basic_data_by_id(context.server_id, user_id)

        return self._reply(
            embed=Embed(
                title=self.__i18n.get(
                    "extensions.mudada.show_exchange_quota_workflow.embed_title",
                    {
                        "name": member.display_name
                    }
                ),
                description=self.__i18n.get(
                    "extensions.mudada.show_exchange_quota_workflow.embed_description",
                    {
                        "remaining_amount": remaining_amount,
                        "exchanged_amount": exchanged_amount,
                        "lost_amount": lost_amount
                    }
                ),
                color=member.color,
                thumbnail_url=member.dominant_avatar_url,
                footer=EmbedFooter(
                    self.__i18n.get(
                        "extensions.mudada.show_exchange_quota_workflow.non_participant_footer"
                    )
                ) if not exchange_quota else None
            )
        )
