from .. import AlertManagerInterface
from ..enums import FrequencyType, PriceDirection
from ..repositories import CryptoRepositoryInterface
from ..utils import is_valid_symbol
from decimal import Decimal, InvalidOperation
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import Choice, CommandResponse, Option, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

ALARM_MIN_PRICE = Decimal("0.00000001")
ALARM_PRICE_UPPER_RATE = Decimal("100")
ALARM_PRICE_LOWER_RATE = Decimal("0.01")

# TODO Expiration for alarms.
# TODO Maximum number of alarms.
@injectable(CommandInterface)
class SetAlarmCommand(CommandBase):
    def __init__(self, alert_manager: AlertManagerInterface, crypto_repository: CryptoRepositoryInterface) -> None:
        super().__init__("set")
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.__crypto_repository: CryptoRepositoryInterface = crypto_repository
        self.group_name = "crypto"
        self.subgroup_name = "alarm"
        self.description = "Sets an alarm for a change in a cryptocurrency's value."
        self.options = [
            Option("symbol", "The symbol, such as BTCEUR.",),
            Option("direction", "The direction of the price change.", choices=[
                Choice("increase to", "ABOVE"),
                Choice("decreases to", "BELOW")
            ]),
            Option("value", "The price to be reached."),
            Option("frequency", "The frequency of alarms.", OptionType.INTEGER),
            Option("frequency_type", "The type of alarm frequency.", choices=[
                Choice("days", "DAYS"),
                Choice("hours", "HOURS"),
                Choice("minutes", "MINUTES")
            ])
        ]

    async def execute(self, context: ServerChatInteractionContext, symbol: str, direction: str,
        value: str, frequency: int, frequency_type: str) -> CommandResponse:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            return CommandResponse(
                action=ReplyAction(content="The symbol you specified isn't in the accepted format.")
            )
        if (pdir := PriceDirection.parse(direction)) is None:
            return CommandResponse(
                action=ReplyAction(content="The direction you specified isn't valid.")
            )
        try:
            decimal_value = Decimal(value)
        except InvalidOperation:
            return CommandResponse(
                action=ReplyAction(content="The value you specified isn't a valid decimal number.")
            )
        if decimal_value < ALARM_MIN_PRICE:
            return CommandResponse(
                action=ReplyAction(content=f"The target price cannot be lower than {ALARM_MIN_PRICE}.")
            )
        if (ftype := FrequencyType.parse(frequency_type)) is None:
            return CommandResponse(
                action=ReplyAction(content="The frequency type you specified isn't valid.")
            )
        if frequency < 0:
            return CommandResponse(
                action=ReplyAction(content="The frequency must be a positive number.")
            )
        price_data = await self.__crypto_repository.get_price(symbol)
        if not price_data:
            return CommandResponse(
                action=ReplyAction(content="I couldn't find that symbol. Did you make a typo?")
            )
        if decimal_value > price_data.price * ALARM_PRICE_UPPER_RATE or decimal_value < price_data.price * ALARM_PRICE_LOWER_RATE:
            return CommandResponse(
                action=ReplyAction(content=f"The target price cannot be more than x{ALARM_PRICE_UPPER_RATE} or x{ALARM_PRICE_LOWER_RATE} of the current price.")
            )
        await self.__alert_manager.add(context.author_id, symbol, pdir, decimal_value, ftype, frequency)
        return CommandResponse(
            action=ReplyAction(content="The alarm has been set.")
        )
