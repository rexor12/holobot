from .. import AlertManagerInterface
from ..enums import PriceDirection
from discord.embeds import Embed
from discord.ext.commands import Context
from discord_slash import SlashContext
from holobot.discord.components import DynamicPager
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import get_author_id
from holobot.sdk.integration import MessagingInterface
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional, Union

@injectable(CommandInterface)
class ViewAlarmsCommand(CommandBase):
    def __init__(self, alert_manager: AlertManagerInterface, log: LogInterface, messaging: MessagingInterface) -> None:
        super().__init__("view")
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.__log: LogInterface = log.with_name("Crypto", "ViewAlarmsCommand")
        self.__messaging: MessagingInterface = messaging
        self.group_name = "crypto"
        self.subgroup_name = "alarm"
        self.description = "Displays your currently set alarms."

    async def execute(self, context: SlashContext) -> None:
        await DynamicPager(self.__messaging, self.__log, context, self.__create_alert_embed)

    async def __create_alert_embed(self, context: Union[Context, SlashContext], page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        alerts = await self.__alert_manager.get_many(get_author_id(context), start_offset, page_size)
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
