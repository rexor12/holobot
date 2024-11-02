from collections.abc import Iterable

from holobot.discord.authorization.repositories import IInteractableAuthorizationRepository
from holobot.discord.sdk.authorization import IAuthorizationDataProvider
from holobot.discord.sdk.workflows.interactables import Interactable
from holobot.discord.sdk.workflows.interactables.restrictions import (
    FeatureRestriction, ServerListRestriction
)
from holobot.sdk.ioc.decorators import injectable

@injectable(IAuthorizationDataProvider)
class AuthorizationDataProvider(IAuthorizationDataProvider):
    def __init__(
        self,
        interactable_authorization_repository: IInteractableAuthorizationRepository
    ) -> None:
        super().__init__()
        self.__authorization_repository = interactable_authorization_repository

    async def is_server_authorized(self, interactable: Interactable, server_id: str) -> bool:
        if not interactable.restrictions:
            return True

        for restriction in interactable.restrictions:
            if isinstance(restriction, FeatureRestriction):
                has_authorization = await self.__authorization_repository.has_authorization(
                    server_id,
                    restriction.feature_name
                )
                if has_authorization is not None:
                    return has_authorization
            elif isinstance(restriction, ServerListRestriction):
                if server_id in restriction.server_ids:
                    return True
            else:
                raise TypeError(f"Unknown restriction type '{type(restriction)}'.")

        return False

    async def get_authorized_server_ids(self, interactable: Interactable) -> Iterable[str]:
        if not interactable.restrictions:
            return ("",)

        server_ids = set[str]()
        for restriction in interactable.restrictions:
            if isinstance(restriction, FeatureRestriction):
                auth_server_ids = await self.__authorization_repository.get_authorized_server_ids(
                    restriction.feature_name
                )
                for server_id in auth_server_ids:
                    server_ids.add(server_id)
            elif isinstance(restriction, ServerListRestriction):
                for server_id in restriction.server_ids:
                    server_ids.add(server_id)
            else:
                raise TypeError(f"Unknown restriction type '{type(restriction)}'.")

        return server_ids
