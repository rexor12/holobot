from holobot.extensions.general.models import Wallet
from holobot.extensions.general.repositories import ICurrencyRepository, IWalletRepository
from holobot.extensions.general.sdk.wallets.exceptions import (
    CurrencyNotFoundException, NotEnoughMoneyException, WalletNotFoundException
)
from holobot.extensions.general.sdk.wallets.managers import IWalletManager
from holobot.extensions.general.sdk.wallets.models import WalletId
from holobot.sdk.ioc.decorators import injectable

_GLOBAL_SERVER_ID = "0"

@injectable(IWalletManager)
class WalletManager(IWalletManager):
    def __init__(
        self,
        currency_repository: ICurrencyRepository,
        wallet_repository: IWalletRepository
    ) -> None:
        super().__init__()
        self.__currency_repository = currency_repository
        self.__wallet_repository = wallet_repository

    async def give_money(
        self,
        user_id: str,
        currency_id: int,
        server_id: str | None,
        amount: int
    ) -> None:
        wallet_id = WalletId(
            user_id=user_id,
            currency_id=currency_id,
            server_id=server_id or _GLOBAL_SERVER_ID
        )
        currency_item = await self.__currency_repository.try_get_by_server(currency_id, wallet_id.server_id, True)
        if not currency_item:
            raise CurrencyNotFoundException(currency_id, server_id)

        wallet = await self.__wallet_repository.get(wallet_id)
        if wallet:
            wallet.amount += amount
            await self.__wallet_repository.update(wallet)
        else:
            wallet = Wallet(
                identifier=wallet_id,
                amount=amount
            )
            await self.__wallet_repository.add(wallet)

    async def take_money(
        self,
        user_id: str,
        currency_id: int,
        server_id: str | None,
        amount: int,
        allow_take_less: bool
    ) -> None:
        wallet_id = WalletId(
            user_id=user_id,
            currency_id=currency_id,
            server_id=server_id or _GLOBAL_SERVER_ID
        )
        currency_item = await self.__currency_repository.try_get_by_server(currency_id, wallet_id.server_id, True)
        if not currency_item:
            raise CurrencyNotFoundException(currency_id, server_id)

        wallet = await self.__wallet_repository.get(wallet_id)
        if not wallet:
            raise WalletNotFoundException(wallet_id)

        if not allow_take_less and wallet.amount < amount:
            raise NotEnoughMoneyException(wallet_id)

        wallet.amount = max(wallet.amount - amount, 0)
        await self.__wallet_repository.update(wallet)
