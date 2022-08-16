from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from ..repositories import CryptoRepositoryInterface
from ..utils import is_valid_symbol

@injectable(IWorkflow)
class ViewPriceWorkflow(WorkflowBase):
    def __init__(self, crypto_repository: CryptoRepositoryInterface) -> None:
        super().__init__()
        self.__crypto_repository: CryptoRepositoryInterface = crypto_repository

    @command(
        description="Gets the latest price information for a symbol.",
        name="price",
        group_name="crypto",
        options=(
            Option("symbol", "The symbol, such as BTCEUR."),
        )
    )
    async def view_price(
        self,
        context: ServerChatInteractionContext,
        symbol: str
    ) -> InteractionResponse:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            return InteractionResponse(
                action=ReplyAction(content="The symbol you specified isn't in the accepted format.")
            )

        price_data = await self.__crypto_repository.get_price(symbol)
        if not price_data:
            return InteractionResponse(
                action=ReplyAction(content="I couldn't find that symbol. Did you make a typo?")
            )

        return InteractionResponse(
            action=ReplyAction(content=Embed(
                title=f"Crypto: {symbol}",
                description=f"Latest price information requested by <@{context.author_id}>.",
                fields=[
                    EmbedField("Price", f"{price_data.price:,.8f}"),
                    EmbedField("Date & time (UTC)", f"{price_data.timestamp:%I:%M:%S %p, %m/%d/%Y}")
                ],
                footer=EmbedFooter("Powered by Binance")
            ))
        )
