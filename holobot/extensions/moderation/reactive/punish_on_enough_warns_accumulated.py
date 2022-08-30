from collections.abc import Callable, Coroutine
from typing import Any

from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.events import CommandProcessedEvent
from holobot.discord.sdk.exceptions import ForbiddenError, ServerNotFoundError, UserNotFoundError
from holobot.discord.sdk.servers.managers import IUserManager
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener
from ..models import WarnSettings
from ..repositories import ILogSettingsRepository, IWarnRepository, IWarnSettingsRepository
from ..workflows.interactables import ModerationCommand
from ..workflows.responses import UserWarnedResponse

@injectable(IListener[CommandProcessedEvent])
class PunishOnEnoughWarnsAccumulated(IListener[CommandProcessedEvent]):
    def __init__(
        self,
        log_settings_repository: ILogSettingsRepository,
        logger_factory: ILoggerFactory,
        messaging: IMessaging,
        user_manager: IUserManager,
        warn_repository: IWarnRepository,
        warn_settings_repository: IWarnSettingsRepository
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(PunishOnEnoughWarnsAccumulated)
        self.__log_settings_repository = log_settings_repository
        self.__messaging = messaging
        self.__user_manager = user_manager
        self.__warn_repository = warn_repository
        self.__warn_settings_repository = warn_settings_repository

    @property
    def priority(self) -> int:
        # This should happen after moderation log entries are written. (#82)
        return 1

    async def on_event(self, event: CommandProcessedEvent):
        if (not issubclass(event.command_type, ModerationCommand)
            or not isinstance(event.response, UserWarnedResponse)):
            return

        warn_settings = await self.__warn_settings_repository.get_by_server(event.server_id)
        if not warn_settings or not warn_settings.has_auto_features:
            return

        warn_count = await self.__warn_repository.get_warn_count_by_user(event.server_id, event.response.user_id)
        is_punished, operation, icon = await self.__try_punish(event.server_id, event.response.user_id, warn_count, warn_settings)
        if not is_punished:
            self.__logger.trace(
                "User has not been punished",
                server_id=event.server_id,
                user_id=event.response.user_id
            )
            return

        self.__logger.trace(
            "User has been punished",
            server_id=event.server_id,
            user_id=event.response.user_id,
            punishment=operation
        )
        server_settings = await self.__log_settings_repository.get_by_server(event.server_id)

        if not server_settings:
            return

        await self.__messaging.send_channel_message(
            event.server_id,
            server_settings.channel_id,
            f":{icon}: <@{event.response.user_id}> has been {operation} automatically for hitting {warn_count} warn strikes."
        )

    async def __try_punish(self, server_id: str, user_id: str, warn_count: int, warn_settings: WarnSettings) -> tuple[bool, str, str]:
        if warn_settings.auto_ban_after > 0 and warn_count >= warn_settings.auto_ban_after:
            is_success = await self.__try_execute_punishment(lambda: self.__user_manager.ban_user(server_id, user_id, self.__get_reason(warn_count)))
            return (is_success, "banned", "no_entry")

        if warn_settings.auto_kick_after > 0 and warn_count >= warn_settings.auto_kick_after:
            is_success = await self.__try_execute_punishment(lambda: self.__user_manager.kick_user(server_id, user_id, self.__get_reason(warn_count)))
            return (is_success, "kicked", "x")

        if warn_settings.auto_mute_after > 0 and warn_count >= warn_settings.auto_mute_after:
            is_success = await self.__try_execute_punishment(lambda: self.__user_manager.silence_user(server_id, user_id, warn_settings.auto_mute_duration))
            return (True, "muted", "mute")

        return (False, "", "")

    async def __try_execute_punishment(self, action: Callable[[], Coroutine[Any, Any, None]]) -> bool:
        try:
            await action()
            return True
        except ForbiddenError:
            self.__logger.debug("Failed to execute punishment as access was forbidden")
            return False
        except ServerNotFoundError:
            self.__logger.debug("Failed to execute punishment as the server was not found")
            return False
        except UserNotFoundError:
            self.__logger.debug("Failed to execute punishment as the user was not found")
            return False

    @staticmethod
    def __get_reason(warn_count: int) -> str:
        return f"You have hit {warn_count} warn strikes which has earned you this punishment."
