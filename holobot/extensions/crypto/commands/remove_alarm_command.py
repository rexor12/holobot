from .. import AlertManagerInterface
from ..utils import is_valid_symbol
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class RemoveAlarmCommand(CommandBase):
    def __init__(self, alert_manager: AlertManagerInterface) -> None:
        super().__init__("remove")
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.group_name = "crypto"
        self.subgroup_name = "alarm"
        self.description = "Removes all of your alarms associated to a symbol."
        self.options = [
            Option("symbol", "The symbol, such as BTCEUR.")
        ]

    async def execute(self, context: ServerChatInteractionContext, symbol: str) -> CommandResponse:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            return CommandResponse(
                action=ReplyAction(content="The symbol you specified isn't in the accepted format.")
            )
        alerts = await self.__alert_manager.remove_many(context.author_id, symbol)
        return CommandResponse(
            action=ReplyAction(content=f"All {len(alerts)} of your alerts set for {symbol} have been removed.")
        )
