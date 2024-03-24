from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.components import Button
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import (
    Cooldown, InteractionResponse, StringOption
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.models import Currency
from holobot.extensions.general.options import EconomicOptions
from holobot.extensions.general.repositories import ICurrencyRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class CreateCurrencyWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        emoji_data_provider: IEmojiDataProvider,
        i18n_provider: II18nProvider,
        options: IOptions[EconomicOptions],
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__emoji_data_provider = emoji_data_provider
        self.__i18n = i18n_provider
        self.__options = options
        self.__unit_of_work_provider = unit_of_work_provider

    @command(
        group_name="economic",
        subgroup_name="currency",
        name="create",
        description="Creates a new custom currency specific to the server.",
        required_permissions=Permission.ADMINISTRATOR,
        cooldown=Cooldown(duration=5),
        defer_type=DeferType.DEFER_MESSAGE_CREATION,
        options=(
            StringOption("name", "The name of the currency.", min_length=1, max_length=60),
            StringOption("emoji", "The emoji that represents the currency.", min_length=1, max_length=60),
            StringOption("description", "An optional description of the currency.", is_mandatory=False, min_length=1, max_length=120)
        )
    )
    async def create_currency(
        self,
        context: InteractionContext,
        name: str,
        emoji: str,
        description: str | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        emoji_data = await self.__emoji_data_provider.find_emoji(emoji, context.server_id)
        if not emoji_data or not emoji_data.identifier or emoji_data.is_animated:
            return self._reply(
                content=self.__i18n.get("extensions.general.create_currency_workflow.invalid_emoji_error")
            )

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            if self.__options.value.MaxCurrencyCountPerServer > 0:
                currency_count = await self.__currency_repository.count_by_server(context.server_id)
                if currency_count >= self.__options.value.MaxCurrencyCountPerServer:
                    return self._reply(
                        content=self.__i18n.get(
                            "extensions.general.create_currency_workflow.too_many_currencies_error"
                        )
                    )

            currency = Currency(
                created_by=context.author_id,
                server_id=context.server_id,
                name=name,
                description=description,
                emoji_id=emoji_data.identifier,
                emoji_name=emoji_data.name
            )
            await self.__currency_repository.add(currency)
            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.create_currency_workflow.currency_created_successfully",
                {
                    "name": currency.name,
                    "emoji_id": currency.emoji_id,
                    "emoji_name": currency.emoji_name
                }
            ),
            components=Button(
                id="gn_currency_view",
                owner_id=context.author_id,
                text=self.__i18n.get("extensions.general.create_currency_workflow.view_currencies_button")
            )
        )
