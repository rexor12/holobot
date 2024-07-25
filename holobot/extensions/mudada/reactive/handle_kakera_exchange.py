import re
from collections.abc import Awaitable

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.events import MessageReceivedEvent
from holobot.extensions.general.sdk.currencies.data_providers import ICurrencyDataProvider
from holobot.extensions.general.sdk.currencies.models import ICurrency
from holobot.extensions.general.sdk.wallets.exceptions import (
    NotEnoughMoneyException, WalletNotFoundException
)
from holobot.extensions.general.sdk.wallets.managers import IWalletManager
from holobot.extensions.mudada.configs import MudadaOptions
from holobot.extensions.mudada.constants import MUDADA_SERVER_ID, MUDAE_USER_ID
from holobot.extensions.mudada.models.exchange_quota import ExchangeQuota
from holobot.extensions.mudada.repositories import IExchangeQuotaRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.database import IUnitOfWorkProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.reactive import IListener

_GIFT_MESSAGE_REGEX = re.compile(r"^<@!?(?P<user_id>\d+)> just gifted \*\*(?P<amount>\d+)\*\*<:kakera:\d+>to <@!?(?P<user_id2>\d+)>$")
_TRADE_MESSAGE_REGEX = re.compile(r"^<@!?(?P<user_id>\d+)>, type the name\(s\) of the character\(s\) you want to trade against \*\*(?P<amount>\d+)\*\*<:kakera:\d+>$")

@injectable(IListener[MessageReceivedEvent])
class HandleKakeraExchange(IListener[MessageReceivedEvent]):
    @property
    def priority(self) -> int:
        return 1000

    def __init__(
        self,
        currency_data_provider: ICurrencyDataProvider,
        exchange_quota_repository: IExchangeQuotaRepository,
        messaging: IMessaging,
        options: IOptions[MudadaOptions],
        unit_of_work_provider: IUnitOfWorkProvider,
        user_data_provider: IUserDataProvider,
        wallet_manager: IWalletManager
    ) -> None:
        super().__init__()
        self.__currency_data_provider = currency_data_provider
        self.__exchange_quota_repository = exchange_quota_repository
        self.__messaging = messaging
        self.__options = options
        self.__unit_of_work_provider = unit_of_work_provider
        self.__user_data_provider = user_data_provider
        self.__wallet_manager = wallet_manager

    async def on_event(self, event: MessageReceivedEvent) -> None:
        if (
            event.message.server_id != MUDADA_SERVER_ID
            or not event.message.author_id == MUDAE_USER_ID
            or not event.message.content
        ):
            return

        # Convert event Kakera into Mudera
        if (
            event.message.channel_id in self.__options.value.KakeraExchangeChannelIds
            and (match := _GIFT_MESSAGE_REGEX.match(event.message.content))
        ):
            await self.__exchange_kakera(event, match)
            return

        # Convert Mudera into regular Kakera.
        if (
            event.interaction
            and event.interaction.name == "collection trade"
            and event.message.channel_id in self.__options.value.MuderaExchangeChannelIds
            and (match := _TRADE_MESSAGE_REGEX.match(event.message.content))
        ):
            await self.__exchange_mudera(event, match)

    async def __exchange_kakera(
        self,
        event: MessageReceivedEvent,
        match: re.Match[str]
    ) -> None:
        # server_id must be validated by the caller
        assert event.message.server_id

        # Gifting but not to Holo
        if (
            not (target_user_id := match.group("user_id2"))
            or not (source_user_id := match.group("user_id"))
            or target_user_id != self.__user_data_provider.get_self().user_id
        ):
            return

        kakera_amount = int(match.group("amount"))
        if kakera_amount < 1:
            return

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            currency = await self.__get_currency_id()
            if currency is None:
                await self.__messaging.send_channel_message(
                    server_id=event.message.server_id,
                    channel_id=event.message.channel_id,
                    content=f"<@{source_user_id}>, the currency associated to the exchange feature cannot be found. Please, ask the moderator team to return your **{kakera_amount:,}** <:kakera:1258854943893360640>."
                )
                return

            exchange_quota = await self.__exchange_quota_repository.get(source_user_id)
            if not exchange_quota:
                exchanged_amount = min(kakera_amount, self.__options.value.ExchangeQuotaPerUser)
                lost_kakera_amount = max(0, kakera_amount - exchanged_amount)
                exchange_quota = ExchangeQuota(
                    identifier=source_user_id,
                    amount=exchanged_amount,
                    exchanged_amount=exchanged_amount,
                    lost_amount=lost_kakera_amount
                )
                await self.__exchange_quota_repository.add(exchange_quota)
            else:
                exchanged_amount = min(kakera_amount, self.__options.value.ExchangeQuotaPerUser - exchange_quota.amount)
                lost_kakera_amount = max(0, kakera_amount - exchanged_amount)
                exchange_quota.amount += exchanged_amount
                exchange_quota.exchanged_amount += exchanged_amount
                exchange_quota.lost_amount += lost_kakera_amount
                await self.__exchange_quota_repository.update(exchange_quota)

            if lost_kakera_amount > 0:
                await self.__messaging.send_channel_message(
                    server_id=event.message.server_id,
                    channel_id=event.message.channel_id,
                    content=f"<@{source_user_id}>, you have exchanged more <:kakera:1258854943893360640> Kakera than you are allowed to. Please, ask the moderator team to return the **{exchange_quota.lost_amount:,}** <:kakera:1258854943893360640> that you've lost so far."
                )

            await self.__wallet_manager.give_money(
                source_user_id,
                currency.identifier,
                event.message.server_id,
                exchanged_amount
            )

            unit_of_work.complete()

        mudera_left = max(0, self.__options.value.ExchangeQuotaPerUser - exchange_quota.amount)
        await self.__messaging.send_channel_message(
            server_id=event.message.server_id,
            channel_id=event.message.channel_id,
            content=f"<@{source_user_id}>, your **{kakera_amount:,}** <:kakera:1258854943893360640> has been exchanged for **{exchanged_amount:,}** <:{currency.emoji_name}:{currency.emoji_id}>. You can still exchange **{mudera_left:,}** <:kakera:1258854943893360640>."
        )

    async def __exchange_mudera(
        self,
        event: MessageReceivedEvent,
        match: re.Match[str]
    ) -> None:
        # interaction and server_id must be validated by the caller
        assert event.interaction
        assert event.message.server_id

        # Trading but not with Holo
        if (
            not (target_user_id := match.group("user_id"))
            or target_user_id != self.__user_data_provider.get_self().user_id
        ):
            return

        kakera_amount = int(match.group("amount")) * 1000
        if kakera_amount < 1:
            return

        async with (unit_of_work := await self.__unit_of_work_provider.create_new()):
            currency = await self.__get_currency_id()
            if currency is None:
                await self.__messaging.send_channel_message(
                    server_id=event.message.server_id,
                    channel_id=event.message.channel_id,
                    content=f"The currency associated to the exchange feature cannot be found. Don't worry, you haven't lost any <:kakera:1258854943893360640> Kakera."
                )
                return

            try:
                await self.__wallet_manager.take_money(
                    event.interaction.author_id,
                    currency.identifier,
                    event.message.server_id,
                    kakera_amount,
                    False
                )
            except (WalletNotFoundException, NotEnoughMoneyException):
                await self.__messaging.send_channel_message(
                    server_id=event.message.server_id,
                    channel_id=event.message.channel_id,
                    content=f"<@{event.interaction.author_id}>, alas, it seems you don't have enough <:{currency.emoji_name}:{currency.emoji_id}> Mudera for this exchange."
                )
                return

            unit_of_work.complete()

        await self.__messaging.send_channel_message(
            server_id=event.message.server_id,
            channel_id=event.message.channel_id,
            content=f"{kakera_amount} ka"
        )

    def __get_currency_id(self) -> Awaitable[ICurrency | None]:
        return self.__currency_data_provider.get_currency_by_code(
            MUDADA_SERVER_ID,
            self.__options.value.MuderaCurrencyCode
        )
