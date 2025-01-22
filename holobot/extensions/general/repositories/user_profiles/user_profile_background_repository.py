from collections.abc import Awaitable
from typing import cast

from holobot.extensions.general.models.items import BackgroundDisplayInfo
from holobot.extensions.general.models.user_profiles import UserProfileBackground
from holobot.sdk.database import IDatabaseManager, IUnitOfWorkProvider
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .iuser_profile_background_repository import IUserProfileBackgroundRepository
from .records import UserProfileBackgroundRecord

@injectable(IUserProfileBackgroundRepository)
class UserProfileBackgroundRepository(
    RepositoryBase[int, UserProfileBackgroundRecord, UserProfileBackground],
    IUserProfileBackgroundRepository
):
    @property
    def record_type(self) -> type[UserProfileBackgroundRecord]:
        return UserProfileBackgroundRecord

    @property
    def model_type(self) -> type[UserProfileBackground]:
        return UserProfileBackground

    @property
    def identifier_type(self) -> type[int]:
        return int

    @property
    def table_name(self) -> str:
        return "user_profile_backgrounds"

    def __init__(
        self,
        database_manager: IDatabaseManager,
        unit_of_work_provider: IUnitOfWorkProvider
    ) -> None:
        super().__init__(database_manager, unit_of_work_provider)

    def get_by_code(self, background_code: str) -> Awaitable[UserProfileBackground | None]:
        return self._get_by_filter(lambda where: where.field(
            "code", Equality.EQUAL, background_code
        ))

    async def get_code(self, background_id: int) -> str | None:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("code")
                .from_table(self.table_name)
                .where()
                .field("id", Equality.EQUAL, background_id)
            )
            result = await query.compile().fetchrow(session.connection)
            if result is None:
                return None

            return result.get("code", None)

    async def get_id_by_code(self, code: str) -> int | None:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("id")
                .from_table(self.table_name)
                .where()
                .field("code", Equality.EQUAL, code)
            )
            result = await query.compile().fetchrow(session.connection)
            if result is None:
                return None

            return result.get("id", None)

    async def get_name_by_code(self, code: str) -> str | None:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("name")
                .from_table(self.table_name)
                .where()
                .field("code", Equality.EQUAL, code)
            )
            result = await query.compile().fetchrow(session.connection)
            if result is None:
                return None

            return result.get("name", None)

    async def get_display_info(
        self,
        background_id: int
    ) -> BackgroundDisplayInfo:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("name")
                .from_table(self.table_name)
                .where()
                .field("id", Equality.EQUAL, background_id)
            )
            if (result := await query.compile().fetchrow(session.connection)) is None:
                raise ValueError(f"Background with identifier '{background_id}' cannot be found.")

            return BackgroundDisplayInfo(
                name=cast(str, result.get("name"))
            )

    def _map_record_to_model(self, record: UserProfileBackgroundRecord) -> UserProfileBackground:
        return UserProfileBackground(
            identifier=record.id.value,
            created_at=record.created_at,
            code=record.code,
            name=record.name
        )

    def _map_model_to_record(self, model: UserProfileBackground) -> UserProfileBackgroundRecord:
        return UserProfileBackgroundRecord(
            id=PrimaryKey(model.identifier),
            created_at=model.created_at,
            code=model.code,
            name=model.name
        )
