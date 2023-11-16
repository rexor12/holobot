from datetime import timedelta

from holobot.extensions.moderation.models import WarnSettings, WarnStrike
from holobot.extensions.moderation.repositories import IWarnRepository, IWarnSettingsRepository
from holobot.sdk.exceptions import ArgumentOutOfRangeError
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.queries import PaginationResult
from holobot.sdk.utils import assert_not_none
from .. import IConfigProvider
from .iwarn_manager import IWarnManager

MIN_WARN_COUNT: int = 1
MAX_WARN_COUNT: int = 20

@injectable(IWarnManager)
class WarnManager(IWarnManager):
    def __init__(
        self,
        config_provider: IConfigProvider,
        warn_repository: IWarnRepository,
        warn_settings_repository: IWarnSettingsRepository
    ) -> None:
        super().__init__()
        self.__config_provider: IConfigProvider = config_provider
        self.__warn_repository: IWarnRepository = warn_repository
        self.__warn_settings_repository: IWarnSettingsRepository = warn_settings_repository

    async def get_warns(
        self,
        server_id: str,
        user_id: str,
        page_index: int,
        page_size: int
    ) -> PaginationResult[WarnStrike]:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        if page_index < 0:
            page_index = 0
        if page_size < 0:
            return PaginationResult(page_index, page_size, 0)

        return await self.__warn_repository.get_warns_by_user(server_id, user_id, page_index, page_size)

    async def warn_user(self, server_id: str, user_id: str, reason: str, warner_id: str) -> WarnStrike:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")
        assert_not_none(reason, "reason")
        assert_not_none(warner_id, "warner_id")

        warn_settings = await self.__warn_settings_repository.get_by_server(server_id)
        decay_threshold = warn_settings and warn_settings.decay_threshold
        warn_strike = WarnStrike(
            server_id=server_id,
            user_id=user_id,
            reason=reason,
            warner_id=warner_id
        )
        warn_strike.identifier = await self.__warn_repository.add_warn(warn_strike, decay_threshold)
        return warn_strike

    async def clear_warns_for_user(self, server_id: str, user_id: str) -> int:
        assert_not_none(server_id, "server_id")
        assert_not_none(user_id, "user_id")

        return await self.__warn_repository.clear_warns_by_user(server_id, user_id)

    async def clear_warns_for_server(self, server_id: str) -> int:
        assert_not_none(server_id, "server_id")

        return await self.__warn_repository.clear_warns_by_server(server_id)

    async def enable_auto_mute(self, server_id: str, warn_count: int, duration: timedelta | None) -> None:
        assert_not_none(server_id, "server_id")

        if warn_count < 1 or warn_count > MAX_WARN_COUNT:
            raise ArgumentOutOfRangeError("warn_count", "1", str(MAX_WARN_COUNT))

        if duration is not None:
            duration_range = self.__config_provider.get_mute_duration_range()
            if not duration in duration_range:
                raise ArgumentOutOfRangeError(
                    "duration",
                    str(duration_range.lower_bound),
                    str(duration_range.upper_bound)
                )

        if warn_settings := await self.__warn_settings_repository.get_by_server(server_id):
            warn_settings.auto_mute_after = warn_count
            warn_settings.auto_mute_duration = duration
            await self.__warn_settings_repository.update(warn_settings)
            return

        await self.__warn_settings_repository.add(WarnSettings(
            server_id=server_id,
            auto_mute_after=warn_count,
            auto_mute_duration=duration
        ))

    async def disable_auto_mute(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        if warn_settings := await self.__warn_settings_repository.get_by_server(server_id):
            warn_settings.auto_mute_after = 0
            warn_settings.auto_mute_duration = None
            await self.__warn_settings_repository.update(warn_settings)

    async def enable_auto_kick(self, server_id: str, warn_count: int) -> None:
        assert_not_none(server_id, "server_id")

        if warn_count < 1 or warn_count > MAX_WARN_COUNT:
            raise ArgumentOutOfRangeError("warn_count", "1", str(MAX_WARN_COUNT))

        if warn_settings := await self.__warn_settings_repository.get_by_server(server_id):
            warn_settings.auto_kick_after = warn_count
            await self.__warn_settings_repository.update(warn_settings)
            return

        await self.__warn_settings_repository.add(WarnSettings(
            server_id=server_id,
            auto_kick_after=warn_count
        ))

    async def disable_auto_kick(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        if warn_settings := await self.__warn_settings_repository.get_by_server(server_id):
            warn_settings.auto_kick_after = 0
            await self.__warn_settings_repository.update(warn_settings)

    async def enable_auto_ban(self, server_id: str, warn_count: int) -> None:
        assert_not_none(server_id, "server_id")

        if warn_count < 1 or warn_count > MAX_WARN_COUNT:
            raise ArgumentOutOfRangeError("warn_count", "1", str(MAX_WARN_COUNT))

        if warn_settings := await self.__warn_settings_repository.get_by_server(server_id):
            warn_settings.auto_ban_after = warn_count
            await self.__warn_settings_repository.update(warn_settings)
            return

        await self.__warn_settings_repository.add(WarnSettings(
            server_id=server_id,
            auto_ban_after=warn_count
        ))

    async def disable_auto_ban(self, server_id: str) -> None:
        assert_not_none(server_id, "server_id")

        if warn_settings := await self.__warn_settings_repository.get_by_server(server_id):
            warn_settings.auto_ban_after = 0
            await self.__warn_settings_repository.update(warn_settings)

    async def get_warn_decay(self, server_id: str) -> timedelta | None:
        assert_not_none(server_id, "server_id")

        warn_settings = await self.__warn_settings_repository.get_by_server(server_id)
        return warn_settings and warn_settings.decay_threshold

    async def set_warn_decay(self, server_id: str, decay_time: timedelta | None) -> None:
        assert_not_none(server_id, "server_id")

        warn_settings = await self.__warn_settings_repository.get_by_server(server_id)
        if decay_time is None:
            if not warn_settings:
                return

            warn_settings.decay_threshold = None
            await self.__warn_settings_repository.update(warn_settings)
            return

        decay_range = self.__config_provider.get_decay_threshold_range()
        if not decay_time in decay_range:
            raise ArgumentOutOfRangeError(
                "decay_time",
                str(decay_range.lower_bound),
                str(decay_range.upper_bound)
            )

        if warn_settings:
            warn_settings.decay_threshold = decay_time
            await self.__warn_settings_repository.update(warn_settings)
            return

        await self.__warn_settings_repository.add(WarnSettings(
            server_id=server_id,
            decay_threshold=decay_time
        ))

    async def remove_warn(self, warn_strike_id: int) -> None:
        await self.__warn_repository.delete(warn_strike_id)
