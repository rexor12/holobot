from holobot.extensions.general.models.items import CurrencyItem, UserItem
from holobot.extensions.general.repositories import ICurrencyRepository, IUserItemRepository
from holobot.extensions.general.sdk.items.exceptions import InvalidItemTypeException
from holobot.extensions.general.sdk.items.models import UserItemId
from holobot.extensions.general.sdk.wallets.exceptions import (
    CurrencyNotFoundException, NotEnoughMoneyException, WalletNotFoundException
)
from holobot.extensions.general.sdk.wallets.managers import IWalletManager
from holobot.sdk.identification import IHoloflakeProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWalletManager)
class WalletManager(IWalletManager):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        holoflake_provider: IHoloflakeProvider,
        user_item_repository: IUserItemRepository
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__holoflake_provider = holoflake_provider
        self.__user_item_repository = user_item_repository

    async def give_money(
        self,
        user_id: int,
        currency_id: int,
        server_id: int,
        amount: int
    ) -> None:
        currency_item = await self.__currency_repository.try_get_by_server(currency_id, server_id, True)
        if not currency_item:
            raise CurrencyNotFoundException(currency_id, server_id)

        wallet = await self.__user_item_repository.get_wallet(user_id, server_id, currency_id)
        if wallet:
            if not isinstance(wallet.item, CurrencyItem):
                raise InvalidItemTypeException(user_id, server_id, currency_id)

            wallet.item.count += amount
            await self.__user_item_repository.update(wallet)
        else:
            await self.__user_item_repository.add(UserItem(
                identifier=UserItemId(
                    server_id=server_id,
                    user_id=user_id,
                    serial_id=self.__holoflake_provider.get_next_id()
                ),
                item=CurrencyItem(
                    count=amount,
                    currency_id=currency_id
                )
            ))

    async def take_money(
        self,
        user_id: int,
        currency_id: int,
        server_id: int,
        amount: int,
        allow_take_less: bool
    ) -> None:
        currency_item = await self.__currency_repository.try_get_by_server(currency_id, server_id, True)
        if not currency_item:
            raise CurrencyNotFoundException(currency_id, server_id)

        wallet = await self.__user_item_repository.get_wallet(user_id, server_id, currency_id)
        if not wallet:
            raise WalletNotFoundException(user_id, server_id, currency_id)

        if not isinstance(wallet.item, CurrencyItem):
            raise InvalidItemTypeException(user_id, server_id, currency_id)

        if not allow_take_less and wallet.item.count < amount:
            raise NotEnoughMoneyException(user_id, server_id, currency_id)

        wallet.item.count = max(wallet.item.count - amount, 0)
        await self.__user_item_repository.update(wallet)
