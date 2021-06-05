from .. import AlertManagerInterface
from ..enums import FrequencyType, PriceDirection
from ..repositories import CryptoRepositoryInterface
from asyncio import TimeoutError
from decimal import Decimal
from discord import Embed
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import cooldown, group
from discord.ext.commands.errors import CommandInvokeError, CommandOnCooldown
from discord.message import Message
from discord_slash.context import SlashContext
from holobot.discord.bot import Bot
from holobot.discord.components import DynamicPager
from typing import Optional, Union

ALARM_MIN_PRICE = Decimal("0.00000001")
ALARM_PRICE_UPPER_RATE = Decimal("100")
ALARM_PRICE_LOWER_RATE = Decimal("0.01")

class Crypto(Cog, name="Crypto"):
    def __init__(self, bot: Bot):
        super().__init__()
        self.__bot = bot
        self.__crypto_repository = self.__bot.service_collection.get(CryptoRepositoryInterface)
        self.__alert_manager = self.__bot.service_collection.get(AlertManagerInterface)

    @group(aliases=["c"], brief="A group of cryptocurrency related commands.")
    async def crypto(self, context: Context):
        if not context.invoked_subcommand:
            await context.send(f"{context.author.mention}, you have to specify a sub-command!", delete_after=3)
    
    @cooldown(1, 10, BucketType.user)
    @crypto.command(aliases=["p"], brief="Gets the latest price information for a symbol (e.g. DOGEBTC).")
    async def price(self, context: Context, symbol: str):
        symbol = symbol.upper()
        if not Crypto.__is_valid_symbol(symbol):
            await context.send(f"{context.author.mention}, you must specify a valid symbol!")
            self.price.reset_cooldown(context)
            return
        price_data = await self.__crypto_repository.get_price(symbol)
        if not price_data:
            await context.send(f"{context.author.mention}, I couldn't find that cryptocurrency.")
            return
        embed = Embed(
            title=f"Crypto: {symbol}",
            description=f"Latest price information requested by {context.author.mention}.",
            color=0xeb7d00
        ).add_field(
            name="Price",
            value=f"{price_data.price:,.8f}",
            inline=True
        ).add_field(
            name="Date & time (UTC)",
            value=f"{price_data.timestamp:%I:%M:%S %p, %m/%d/%Y}",
            inline=True
        ).set_footer(
            text=f"Powered by Binance"
        )
        await context.send(embed=embed)
    
    # TODO Expiration for alarms.
    # TODO Maximum number of alarms.
    @cooldown(1, 10, BucketType.user)
    @crypto.command(name="setalarm", aliases=["sa"], brief="Sets an alarm for a change in a cryptocurrency's value.")
    async def set_alarm(self, context: Context, symbol: str, direction: str, value: Decimal,
        frequency_type: str, frequency: int):
        symbol = symbol.upper()
        if not Crypto.__is_valid_symbol(symbol):
            await context.send(f"{context.author.mention}, you must specify a valid symbol!")
            self.set_alarm.reset_cooldown(context)
            return
        if (pdir := PriceDirection.parse(direction)) is None:
            await context.send(f"{context.author.mention}, you must specify a valid direction!")
            self.set_alarm.reset_cooldown(context)
            return
        if value < ALARM_MIN_PRICE:
            await context.send(f"{context.author.mention}, the target price cannot be lower than {ALARM_MIN_PRICE}!")
            self.set_alarm.reset_cooldown(context)
            return
        if (ftype := FrequencyType.parse(frequency_type)) is None:
            await context.send(f"{context.author.mention}, you must specify a valid frequency type!")
            self.set_alarm.reset_cooldown(context)
            return
        if frequency < 0:
            await context.send(f"{context.author.mention}, the frequency must be a positive number!")
            self.set_alarm.reset_cooldown(context)
            return
        price_data = await self.__crypto_repository.get_price(symbol)
        if not price_data:
            await context.send(f"{context.author.mention}, I couldn't find that cryptocurrency!")
            self.set_alarm.reset_cooldown(context)
            return
        if value > price_data.price * ALARM_PRICE_UPPER_RATE or value < price_data.price * ALARM_PRICE_LOWER_RATE:
            await context.send(f"{context.author.mention}, the target price cannot be more than x{ALARM_PRICE_UPPER_RATE} or x{ALARM_PRICE_LOWER_RATE} of the current price!")
            self.set_alarm.reset_cooldown(context)
            return
        await self.__alert_manager.add(str(context.author.id), symbol, pdir, value, ftype, frequency)
        await context.send(f"{context.author.mention}, the alarm for {symbol} going {str(pdir)} the price of {value} has been set. It will expire at -datetime-.")
    
    @cooldown(1, 60, BucketType.user)
    @crypto.command(name="viewalarms", aliases=["va"], brief="Displays your currently set alarms.")
    async def view_alarms(self, context: Context):
        await DynamicPager(self.__bot, context, self.__create_alert_embed)
    
    @cooldown(1, 120, BucketType.user)
    @crypto.command(name="clearalarm", aliases=["ca"], brief="Clears all alarms associated to a symbol.")
    async def clear_alarm(self, context: Context, symbol: str):
        symbol = symbol.upper()
        if not Crypto.__is_valid_symbol(symbol):
            await context.send(f"{context.author.mention}, you must specify a valid symbol!")
            self.set_alarm.reset_cooldown(context)
            return
        alerts = await self.__alert_manager.remove_many(str(context.author.id), symbol)
        await context.send(f"{context.author.mention}, {len(alerts)} alarms for {symbol} have been removed.")

    @cooldown(1, 120, BucketType.user)
    @crypto.command(name="purgealarms", aliases=["pa"], brief="Clears ALL alarms of ALL symbols.")
    async def purge_alarms(self, context: Context):
        await context.send(f"{context.author.mention}, **__ALL__** of your alarms will be removed. Type 'confirm' if you're sure about this.")
        def check_message(message: Message) -> bool:
            return (message.author == context.author
                    and message.channel == context.channel)
        
        try:
            response_message: Message = await self.__bot.wait_for('message', check=check_message, timeout=30)
            if not response_message or not response_message.content == "confirm":
                await context.send(f"{context.author.mention}, your alarms won't be purged.")
                return
            await self.__alert_manager.remove_all(str(context.author.id))
            await context.send(f"{context.author.mention}, your alarms have been purged.")
        except TimeoutError:
            pass

    @staticmethod
    def __is_valid_symbol(symbol: str) -> bool:
        return symbol is not None and len(symbol) >= 4

    async def __create_alert_embed(self, context: Union[Context, SlashContext], page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        alerts = await self.__alert_manager.get_many(context.author.id, start_offset, page_size)
        if len(alerts) == 0:
            return None
        
        embed = Embed(
            title="Crypto alarms",
            description=f"Cryptocurrency alarms of {context.author.mention}.",
            color=0xeb7d00
        )
        for alert in alerts:
            arrow = "🔼" if alert.direction == PriceDirection.ABOVE else "🔽"
            embed.add_field(
                name=alert.symbol,
                value=f"{arrow} {alert.price:,.8f}",
                inline=False
            )
        return embed

    # TODO Implement a decorator for handling specific exception types to avoid duplication. Eg. @price.error.CommandOnCooldown
    @price.error
    @set_alarm.error
    @view_alarms.error
    @clear_alarm.error
    @purge_alarms.error
    async def on_error(self, context: Context, error):
        if isinstance(error, CommandOnCooldown):
            await context.send(f"{context.author.mention}, you're too fast! ({int(error.retry_after)} seconds cooldown)", delete_after=5)
            return
        if isinstance(error, CommandInvokeError) and isinstance(error.original, ConnectionRefusedError):
            await context.send(f"{context.author.mention}, I'm unable to complete your request due to an internal error. Please, try again later.", delete_after=5)
            return
        raise error

def setup(bot: Bot):
    bot.add_cog(Crypto(bot))
