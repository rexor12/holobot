from holobot.discord.sdk.actions.enums import DeferType
from holobot.discord.sdk.enums import Permission
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import autocomplete, command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    AutocompleteOption, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.models.items import CurrencyItem, UserItem
from holobot.extensions.general.repositories import ICurrencyRepository, IUserItemRepository
from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.extensions.general.workflows.economic.utils import get_currency_autocomplete_choices
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.identification import IHoloflakeProvider
from holobot.sdk.ioc.decorators import injectable

_MONEY_AMOUNT_MAX: int = 1_000_000_000
_AUTOCOMPLETE_COUNT_MAX: int = 5

@injectable(IWorkflow)
class GiveMoneyWorkflow(WorkflowBase):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        holoflake_provider: IHoloflakeProvider,
        i18n_provider: II18nProvider,
        unit_of_work_provider: IUnitOfWorkProvider,
        user_item_repository: IUserItemRepository
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__holoflake_provider = holoflake_provider
        self.__i18n = i18n_provider
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_item_repository = user_item_repository

    @command(
        group_name="economic",
        subgroup_name="money",
        name="give",
        description="Gives the specified amount of money to a user of your choice.",
        options=(
            Option("user", "The user you'd like to give money to.", OptionType.USER),
            Option("amount", "The amount of money you'd like to give.", OptionType.INTEGER),
            Option("currency", "The type of money you'd like to give.", OptionType.STRING, is_autocomplete=True)
        ),
        required_permissions=Permission.ADMINISTRATOR,
        defer_type=DeferType.DEFER_MESSAGE_CREATION
    )
    async def give_money(
        self,
        context: InteractionContext,
        user: int,
        amount: int,
        currency: str
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(content=self.__i18n.get("interactions.server_only_interaction_error"))

        if amount > _MONEY_AMOUNT_MAX:
            return self._reply(
                content=self.__i18n.get(
                    "extensions.general.give_money_workflow.too_much_money_error",
                    {
                        "max_amount": _MONEY_AMOUNT_MAX
                    }
                )
            )

        currency_id = int(currency)
        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            currency_item = await self.__currency_repository.try_get_by_server(currency_id, context.server_id, False)
            if not currency_item:
                return self._reply(
                    content=self.__i18n.get("extensions.general.give_money_workflow.invalid_currency_error")
                )

            wallet = await self.__user_item_repository.get_wallet(
                user,
                context.server_id,
                currency_id
            )
            if wallet:
                wallet.item.count += amount
                await self.__user_item_repository.update(wallet)
            else:
                wallet = UserItem(
                    identifier=UserItemId(
                        server_id=context.server_id,
                        user_id=user,
                        serial_id=self.__holoflake_provider.get_next_id()
                    ),
                    item=CurrencyItem(
                        count=amount,
                        currency_id=currency_id
                    )
                )
                await self.__user_item_repository.add(wallet)

            unit_of_work.complete()

        return self._reply(
            content=self.__i18n.get(
                "extensions.general.give_money_workflow.successfully_gave_money",
                {
                    "user_id": wallet.identifier.user_id,
                    "amount": wallet.item.count,
                    "emoji_id": currency_item.emoji_id,
                    "emoji_name": currency_item.emoji_name
                }
            ),
            suppress_user_mentions=True
        )

    @autocomplete(
        group_name="economic",
        subgroup_name="money",
        command_name="give",
        options=("currency",)
    )
    async def autocomplete_currency(
        self,
        context: InteractionContext,
        options: tuple[AutocompleteOption, ...],
        target_option: AutocompleteOption
    ) -> InteractionResponse:
        return self._autocomplete(
            await get_currency_autocomplete_choices(
                context,
                options,
                target_option,
                _AUTOCOMPLETE_COUNT_MAX,
                self.__currency_repository,
                False
            )
        )
