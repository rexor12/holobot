from collections.abc import Awaitable

from holobot.extensions.general.models import FortuneCookie
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .ifortune_cookie_repository import IFortuneCookieRepository
from .records import FortuneCookieRecord

@injectable(IFortuneCookieRepository)
class FortuneCookieRepository(
    RepositoryBase[int, FortuneCookieRecord, FortuneCookie],
    IFortuneCookieRepository
):
    @property
    def record_type(self) -> type[FortuneCookieRecord]:
        return FortuneCookieRecord

    @property
    def model_type(self) -> type[FortuneCookie]:
        return FortuneCookie

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "fortune_cookies"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    async def get_random(self) -> FortuneCookie | None:
        results = await self._get_many_by_function("get_fortune_cookie")

        return results[0] if results else None

    def _map_record_to_model(self, record: FortuneCookieRecord) -> FortuneCookie:
        return FortuneCookie(
            identifier=record.id.value,
            message=record.message
        )

    def _map_model_to_record(self, model: FortuneCookie) -> FortuneCookieRecord:
        return FortuneCookieRecord(
            id=PrimaryKey(model.identifier),
            message=model.message
        )
