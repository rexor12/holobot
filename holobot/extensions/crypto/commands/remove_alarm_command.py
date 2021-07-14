from .. import AlertManagerInterface
from ..utils import is_valid_symbol
from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id, reply
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
            create_option("symbol", "The symbol, such as BTCEUR.", SlashCommandOptionType.STRING, True)
        ]

    async def execute(self, context: SlashContext, symbol: str) -> None:
        symbol = symbol.upper()
        if not is_valid_symbol(symbol):
            await reply(context, "The symbol you specified isn't in the accepted format.")
            return
        alerts = await self.__alert_manager.remove_many(get_author_id(context), symbol)
        await reply(context, f"All {len(alerts)} of your alerts set for {symbol} have been removed.")
