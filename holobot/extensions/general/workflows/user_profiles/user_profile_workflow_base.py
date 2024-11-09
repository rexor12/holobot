from datetime import timedelta

from holobot.discord.sdk.data_providers import IUserDataProvider
from holobot.discord.sdk.workflows import WorkflowBase
from holobot.extensions.general.factories import IUserProfileFactory
from holobot.extensions.general.models.user_profiles import UserProfile
from holobot.sdk.caching import AbsoluteExpirationCacheEntryPolicy, IObjectCache
from holobot.sdk.network import IHttpClientPool
from holobot.sdk.utils.datetime_utils import utcnow

_EXPIRATION_TIME = timedelta(minutes=10)

class UserProfileWorkflowBase(WorkflowBase):
    def __init__(
        self,
        cache: IObjectCache,
        http_client_pool: IHttpClientPool,
        user_data_provider: IUserDataProvider,
        user_profile_factory: IUserProfileFactory
    ) -> None:
        super().__init__()
        self._cache = cache
        self._http_client_pool = http_client_pool
        self._user_data_provider = user_data_provider
        self._user_profile_factory = user_profile_factory

    async def _generate_user_profile(
        self,
        user_id: int,
        user_profile: UserProfile,
        custom_background_code: str | None = None
    ) -> bytes:
        user_data = await self._user_data_provider.get_user_data_by_id(user_id)
        avatar_bytes: bytes | None = None
        if user_data.avatar_url_small:
            avatar_url = user_data.avatar_url_small
            cached_avatar = await self._cache.get_or_add(
                f"UserProfile/Avatar/{user_data.user_id}",
                lambda _: self._http_client_pool.get_raw(avatar_url),
                AbsoluteExpirationCacheEntryPolicy(expires_at=utcnow() + _EXPIRATION_TIME)
            )
            if isinstance(cached_avatar, bytes):
                avatar_bytes = cached_avatar

        return self._user_profile_factory.create_profile_image(
            user_data.name,
            user_profile,
            avatar_bytes,
            custom_background_code
        )
