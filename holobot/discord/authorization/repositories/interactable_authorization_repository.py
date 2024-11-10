from collections.abc import Iterable

from holobot.discord.authorization.models import (
    InteractableAuthorization, InteractableAuthorizationId
)
from holobot.sdk.database.entities import PrimaryKey
from holobot.sdk.database.queries import Query
from holobot.sdk.database.queries.enums import Connector, Equality
from holobot.sdk.database.repositories import RepositoryBase
from holobot.sdk.ioc.decorators import injectable
from .iinteractable_authorization_repository import IInteractableAuthorizationRepository
from .records import InteractableAuthorizationRecord

@injectable(IInteractableAuthorizationRepository)
class InteractableAuthorizationRepository(
    RepositoryBase[InteractableAuthorizationId, InteractableAuthorizationRecord, InteractableAuthorization],
    IInteractableAuthorizationRepository
):
    @property
    def record_type(self) -> type[InteractableAuthorizationRecord]:
        return InteractableAuthorizationRecord

    @property
    def model_type(self) -> type[InteractableAuthorization]:
        return InteractableAuthorization

    @property
    def identifier_type(self) -> type[InteractableAuthorizationId]:
        return InteractableAuthorizationId

    @property
    def table_name(self) -> str:
        return "interactable_authorizations"

    async def has_authorization(
        self,
        server_id: int,
        interactable_id: str
    ) -> bool | None:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("status")
                .from_table(self.table_name)
                .where()
                .fields(
                    Connector.AND,
                    ("interactable_id", Equality.EQUAL, interactable_id),
                    ("server_id", Equality.EQUAL, server_id)
                )
            )
            result = await query.compile().fetchval(session.connection)
            if result is None or not isinstance(result, bool):
                return None

            return result

    async def get_authorized_server_ids(
        self,
        interactable_id: str
    ) -> Iterable[int]:
        async with (session := await self._get_session()):
            query = (Query
                .select()
                .columns("server_id")
                .from_table(self.table_name)
                .where()
                .field("interactable_id", Equality.EQUAL, interactable_id)
            )
            results = await query.compile().fetch(session.connection)

            return map(lambda i: i.get("server_id", 0), results)

    def _map_record_to_model(self, record: InteractableAuthorizationRecord) -> InteractableAuthorization:
        return InteractableAuthorization(
            identifier=InteractableAuthorizationId(
                interactable_id=record.interactable_id.value,
                server_id=record.server_id.value
            ),
            status=record.status
        )

    def _map_model_to_record(
        self,
        model: InteractableAuthorization
    ) -> InteractableAuthorizationRecord:
        return InteractableAuthorizationRecord(
            interactable_id=PrimaryKey(model.identifier.interactable_id),
            server_id=PrimaryKey(model.identifier.server_id),
            status=model.status
        )
