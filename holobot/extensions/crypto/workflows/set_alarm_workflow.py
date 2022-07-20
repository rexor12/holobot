from .. import AlertManagerInterface
from ..enums import FrequencyType, PriceDirection
from ..repositories import CryptoRepositoryInterface
from ..utils import is_valid_symbol
from decimal import Decimal, InvalidOperation
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

ALARM_MIN_PRICE = Decimal("0.00000001")
ALARM_PRICE_UPPER_RATE = Decimal("100")
ALARM_PRICE_LOWER_RATE = Decimal("0.01")

# TODO Expiration for alarms.
# TODO Maximum number of alarms.
@injectable(IWorkflow)
class SetAlarmWorkflow(WorkflowBase):
    def __init__(
        self,
        alert_manager: AlertManagerInterface,
        crypto_repository: CryptoRepositoryInterface
    ) -> None:
        super().__init__()
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.__crypto_repository: CryptoRepositoryInterface = crypto_repository

    @command(
        description="Sets an alarm for a change in a cryptocurrency's value.",
        name="set",
        group_name="crypto",
        subgroup_name="alarm",
        options=(
            Option("symbol", "The symbol, such as BTCEUR.",),
            Option("direction", "The direction of the price change.", choices=(
                Choice("increase to", "ABOVE"),
                Choice("decreases to", "BELOW")
            )),
            Option("value", "The price to be reached."),
            Option("frequency", "The frequency of alarms.", OptionType.INTEGER),
            Option("frequency_type", "The type of alarm frequency.", choices=(
                Choice("days", "DAYS"),
                Choice("hours", "HOURS"),
                Choice("minutes", "MINUTES")
            ))
        )
    )
    async def set_alarm(
        self,
        context: ServerChatInteractionContext,
        symbol: str,
        direction: str,
        value: str,
        frequency: int,
        frequency_type: str
    ) -> InteractionResponse:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            return InteractionResponse(
                action=ReplyAction(content="The symbol you specified isn't in the accepted format.")
            )
        if (pdir := PriceDirection.parse(direction)) is None:
            return InteractionResponse(
                action=ReplyAction(content="The direction you specified isn't valid.")
            )
        try:
            decimal_value = Decimal(value)
        except InvalidOperation:
            return InteractionResponse(
                action=ReplyAction(content="The value you specified isn't a valid decimal number.")
            )
        if decimal_value < ALARM_MIN_PRICE:
            return InteractionResponse(
                action=ReplyAction(content=f"The target price cannot be lower than {ALARM_MIN_PRICE}.")
            )
        if (ftype := FrequencyType.parse(frequency_type)) is None:
            return InteractionResponse(
                action=ReplyAction(content="The frequency type you specified isn't valid.")
            )
        if frequency < 0:
            return InteractionResponse(
                action=ReplyAction(content="The frequency must be a positive number.")
            )
        price_data = await self.__crypto_repository.get_price(symbol)
        if not price_data:
            return InteractionResponse(
                action=ReplyAction(content="I couldn't find that symbol. Did you make a typo?")
            )
        if decimal_value > price_data.price * ALARM_PRICE_UPPER_RATE or decimal_value < price_data.price * ALARM_PRICE_LOWER_RATE:
            return InteractionResponse(
                action=ReplyAction(content=f"The target price cannot be more than x{ALARM_PRICE_UPPER_RATE} or x{ALARM_PRICE_LOWER_RATE} of the current price.")
            )
        await self.__alert_manager.add(context.author_id, symbol, pdir, decimal_value, ftype, frequency)
        return InteractionResponse(
            action=ReplyAction(content="The alarm has been set.")
        )