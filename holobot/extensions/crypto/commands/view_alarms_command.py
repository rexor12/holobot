from .. import AlertManagerInterface
from ..enums import PriceDirection
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.components import Pager
from holobot.discord.sdk.models import Embed, EmbedField
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from typing import Optional, Union

@injectable(CommandInterface)
class ViewAlarmsCommand(CommandBase):
    def __init__(self, alert_manager: AlertManagerInterface, log: LogInterface, messaging: IMessaging) -> None:
        super().__init__("view")
        self.__alert_manager: AlertManagerInterface = alert_manager
        self.__log: LogInterface = log.with_name("Crypto", "ViewAlarmsCommand")
        self.__messaging: IMessaging = messaging
        self.group_name = "crypto"
        self.subgroup_name = "alarm"
        self.description = "Displays your currently set alarms."

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        await Pager(self.__messaging, self.__log, context, self.__create_alert_embed)
        return CommandResponse()

    async def __create_alert_embed(self, context: ServerChatInteractionContext, page: int, page_size: int) -> Optional[Embed]:
        start_offset = page * page_size
        alerts = await self.__alert_manager.get_many(context.author_id, start_offset, page_size)
        if len(alerts) == 0:
            return None
        
        embed = Embed(
            title="Crypto alarms",
            description=f"Cryptocurrency alarms of <@{context.author_id}>."
        )
        for alert in alerts:
            arrow = "🔼" if alert.direction == PriceDirection.ABOVE else "🔽"
            embed.fields.append(EmbedField(
                name=alert.symbol,
                value=f"{arrow} {alert.price:,.8f}",
                is_inline=False
            ))
        return embed
