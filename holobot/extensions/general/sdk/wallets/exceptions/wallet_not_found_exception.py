from holobot.extensions.general.sdk.wallets.models import WalletId

class WalletNotFoundException(Exception):
    @property
    def wallet_id(self) -> WalletId:
        return self.__wallet_id

    def __init__(
        self,
        wallet_id: WalletId,
        message: str | None = None
    ) -> None:
        super().__init__(message)
        self.__wallet_id = wallet_id
