from datetime import timedelta

from holobot.sdk.caching import IObjectCache, SlidingExpirationCacheEntryPolicy
from holobot.sdk.database import AggregateRoot
from holobot.sdk.database.repositories.ientity_cache import IEntityCache, _TEntity, _TIdentifier
from holobot.sdk.exceptions import ArgumentError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import UndefinedType

_DEFAULT_EXPIRATION: timedelta = timedelta(minutes=5)

@injectable(IEntityCache)
class EntityCache(IEntityCache):
    def __init__(
        self,
        cache: IObjectCache
    ) -> None:
        super().__init__()
        self.__cache = cache

    async def get(self, entity_type: type[_TEntity], identifier: _TIdentifier) -> _TEntity | None:
        cache_key = EntityCache.__get_cache_key(entity_type, identifier)
        entity = await self.__cache.get(cache_key)

        return None if isinstance(entity, UndefinedType) else entity

    async def set(self, entity: AggregateRoot[_TIdentifier]) -> None:
        cache_key = EntityCache.__get_cache_key(type(entity), entity.identifier)

        await self.__cache.add_or_replace(
            cache_key,
            entity,
            SlidingExpirationCacheEntryPolicy(_DEFAULT_EXPIRATION)
        )

    async def invalidate(self, entity_type: type[_TEntity], identifier: _TIdentifier) -> None:
        cache_key = EntityCache.__get_cache_key(entity_type, identifier)

        await self.__cache.remove(cache_key)

    @staticmethod
    def __get_cache_key(entity_type: type[_TEntity], identifier: _TIdentifier) -> str:
        if not isinstance(identifier, (int, str)):
            raise ArgumentError("identifier", "Entity identifier must be either an integer or a string.")

        return f"entity/{entity_type.__name__}/{str(identifier)}"
