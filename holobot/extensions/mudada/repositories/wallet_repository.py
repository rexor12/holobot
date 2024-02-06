
from holobot.extensions.mudada.models import Wallet
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .iwallet_repository import IWalletRepository
from .records import WalletRecord

@injectable(IWalletRepository)
class WalletRepository(
    RepositoryBase[str, WalletRecord, Wallet],
    IWalletRepository
):
    @property
    def record_type(self) -> type[WalletRecord]:
        return WalletRecord

    @property
    def model_type(self) -> type[Wallet]:
        return Wallet

    @property
    def table_name(self) -> str:
        return "mudada_wallets"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def remove_from_all_users(self, amount: int) -> None:
        async with (session := await self._get_session()):
            await session.connection.execute(
                f"UPDATE {self.table_name} SET amount = CASE WHEN amount >= $1 THEN amount - $1 ELSE 0 END",
                amount
            )

    def _map_record_to_model(self, record: WalletRecord) -> Wallet:
        return Wallet(
            identifier=record.id,
            amount=record.amount
        )

    def _map_model_to_record(self, model: Wallet) -> WalletRecord:
        return WalletRecord(
            id=model.identifier,
            amount=model.amount
        )
