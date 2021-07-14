from .. import AlertManagerInterface
from ..enums import FrequencyType, PriceDirection
from ..repositories import CryptoRepositoryInterface
from ..utils import is_valid_symbol
from decimal import Decimal, InvalidOperation
from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id, reply
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
            create_option("symbol", "The symbol, such as BTCEUR.", SlashCommandOptionType.STRING, True),
            create_option("direction", "The direction of the price change.", SlashCommandOptionType.STRING, True, choices=[
                create_choice("ABOVE", "increase to"),
                create_choice("BELOW", "decreases to")
            ]),
            create_option("value", "The price to be reached.", SlashCommandOptionType.STRING, True),
            create_option("frequency", "The frequency of alarms.", SlashCommandOptionType.INTEGER, True),
            create_option("frequency_type", "The type of alarm frequency.", SlashCommandOptionType.STRING, True, choices=[
                create_choice("DAYS", "days"),
                create_choice("HOURS", "hours"),
                create_choice("MINUTES", "minutes")
            ])
        ]

    async def execute(self, context: SlashContext, symbol: str, direction: str,
        value: str, frequency_type: str, frequency: int) -> None:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            await reply(context, "The symbol you specified isn't in the accepted format.")
            return
        if (pdir := PriceDirection.parse(direction)) is None:
            await reply(context, "The direction you specified isn't valid.")
            return
        try:
            decimal_value = Decimal(value)
        except InvalidOperation:
            await reply(context, "The value you specified isn't a valid decimal number.")
            return
        if decimal_value < ALARM_MIN_PRICE:
            await reply(context, f"The target price cannot be lower than {ALARM_MIN_PRICE}.")
            return
        if (ftype := FrequencyType.parse(frequency_type)) is None:
            await reply(context, "The frequency type you specified isn't valid.")
            return
        if frequency < 0:
            await reply(context, "The frequency must be a positive number.")
            return
        price_data = await self.__crypto_repository.get_price(symbol)
        if not price_data:
            await reply(context, "I couldn't find that symbol. Did you make a typo?")
            return
        if decimal_value > price_data.price * ALARM_PRICE_UPPER_RATE or decimal_value < price_data.price * ALARM_PRICE_LOWER_RATE:
            await reply(context, f"The target price cannot be more than x{ALARM_PRICE_UPPER_RATE} or x{ALARM_PRICE_LOWER_RATE} of the current price.")
            return
        await self.__alert_manager.add(get_author_id(context), symbol, pdir, decimal_value, ftype, frequency)
        await reply(context, "The alarm has been set.")
