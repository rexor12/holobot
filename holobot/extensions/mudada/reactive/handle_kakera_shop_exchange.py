import re

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.events import MessageReceivedEvent
from holobot.extensions.mudada.constants import MUDAE_USER_ID
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.reactive import IListener

# <@857399092875362314>, type the name(s) of the character(s) you want to trade against **1**<:kakera:469835869059153940>
# _GIVEKAKERA_MESSAGE_REGEX = re.compile(r"^<@!?(?P<user_id1>\d+)> just gifted \*\*(?P<amount>\d)\*\*<:kakera:\d+>to <@!?(?P<user_id2>\d+)>$")
_TRADE_MESSAGE_REGEX = re.compile(r"^<@!?(?P<user_id>\d+)>, type the name\(s\) of the character\(s\) you want to trade against \*\*(?P<amount>\d)\*\*<:kakera:\d+>$")

@injectable(IListener[MessageReceivedEvent])
class HandleKakeraShopExchange(IListener[MessageReceivedEvent]):
    @property
    def priority(self) -> int:
        return 1000

    def __init__(
        self,
        messaging: IMessaging,
        user_data_provider: IUserDataProvider
    ) -> None:
        super().__init__()
        self.__messaging = messaging
        self.__user_data_provider = user_data_provider

    async def on_event(self, event: MessageReceivedEvent) -> None:
        if (
            not event.interaction
            or not event.message.author_id == MUDAE_USER_ID
            or not event.message.content
            or not event.message.server_id
            or not event.interaction.name == "collection trade"
            or not (match := _TRADE_MESSAGE_REGEX.match(event.message.content))
            or not (target_user_id := match.group("user_id"))
            or target_user_id != self.__user_data_provider.get_self().user_id
        ):
            return

        await self.__messaging.send_channel_message(
            server_id=event.message.server_id,
            channel_id=event.message.channel_id,
            content=f"20 ka"
        )
