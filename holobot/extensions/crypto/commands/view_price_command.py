from ..repositories import CryptoRepositoryInterface
from ..utils import is_valid_symbol
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ViewPriceCommand(CommandBase):
    def __init__(self, crypto_repository: CryptoRepositoryInterface) -> None:
        super().__init__("price")
        self.__crypto_repository: CryptoRepositoryInterface = crypto_repository
        self.group_name = "crypto"
        self.description = "Gets the latest price information for a symbol."
        self.options = [
            Option("symbol", "The symbol, such as BTCEUR.")
        ]

    async def execute(self, context: ServerChatInteractionContext, symbol: str) -> CommandResponse:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            return CommandResponse(
                action=ReplyAction(content="The symbol you specified isn't in the accepted format.")
            )
        
        price_data = await self.__crypto_repository.get_price(symbol)
        if not price_data:
            return CommandResponse(
                action=ReplyAction(content="I couldn't find that symbol. Did you make a typo?")
            )

        return CommandResponse(
            action=ReplyAction(content=Embed(
                title=f"Crypto: {symbol}",
                description=f"Latest price information requested by <@{context.author_id}>.",
                fields=[
                    EmbedField("Price", f"{price_data.price:,.8f}"),
                    EmbedField("Date & time (UTC)", f"{price_data.timestamp:%I:%M:%S %p, %m/%d/%Y}")
                ],
                footer=EmbedFooter(f"Powered by Binance")
            ))
        )
