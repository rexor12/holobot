
from holobot.extensions.mudada.models import ExchangeQuota
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .iexchange_quota_repository import IExchangeQuotaRepository
from .records import ExchangeQuotaRecord

@injectable(IExchangeQuotaRepository)
class ExchangeQuotaRepository(
    RepositoryBase[str, ExchangeQuotaRecord, ExchangeQuota],
    IExchangeQuotaRepository
):
    @property
    def record_type(self) -> type[ExchangeQuotaRecord]:
        return ExchangeQuotaRecord

    @property
    def model_type(self) -> type[ExchangeQuota]:
        return ExchangeQuota

    @property
    def identifier_type(self) -> type[str]:
        return str

    @property
    def table_name(self) -> str:
        return "mudada_exchange_quotas"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def _map_record_to_model(self, record: ExchangeQuotaRecord) -> ExchangeQuota:
        return ExchangeQuota(
            identifier=record.id.value,
            amount=record.amount,
            exchanged_amount=record.exchanged_amount,
            lost_amount=record.lost_amount
        )

    def _map_model_to_record(self, model: ExchangeQuota) -> ExchangeQuotaRecord:
        return ExchangeQuotaRecord(
            id=PrimaryKey(model.identifier),
            amount=model.amount,
            exchanged_amount=model.exchanged_amount,
            lost_amount=model.lost_amount
        )
