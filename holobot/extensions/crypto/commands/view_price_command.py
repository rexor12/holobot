from ..repositories import CryptoRepositoryInterface
from ..utils import is_valid_symbol
from discord.embeds import Embed
from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ViewPriceCommand(CommandBase):
    def __init__(self, crypto_repository: CryptoRepositoryInterface) -> None:
        super().__init__("price")
        self.__crypto_repository: CryptoRepositoryInterface = crypto_repository
        self.group_name = "crypto"
        self.description = "Gets the latest price information for a symbol."
        self.options = [
            create_option("symbol", "The symbol, such as BTCEUR.", SlashCommandOptionType.STRING, True)
        ]

    async def execute(self, context: SlashContext, symbol: str) -> None:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            await reply(context, "The symbol you specified isn't in the accepted format.")
            return
        
        price_data = await self.__crypto_repository.get_price(symbol)
        if not price_data:
            await reply(context, "I couldn't find that symbol. Did you make a typo?")
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
        await reply(context, embed)
