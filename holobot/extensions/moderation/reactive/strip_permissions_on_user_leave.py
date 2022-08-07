from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError
from holobot.discord.sdk.events import ServerMemberLeftEvent
from holobot.extensions.moderation.managers import ILogManager, IPermissionManager
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener

@injectable(IListener[ServerMemberLeftEvent])
class StripPermissionsOnUserLeave(IListener[ServerMemberLeftEvent]):
    def __init__(
        self,
        log_manager: ILogManager,
        logger_factory: ILoggerFactory,
        permission_manager: IPermissionManager
    ) -> None:
        super().__init__()
        self.__log_manager = log_manager
        self.__logger = logger_factory.create(StripPermissionsOnUserLeave)
        self.__permission_manager = permission_manager

    @property
    def priority(self) -> int:
        # This should happen after moderation log entries are written. (#82)
        return 1

    async def on_event(self, event: ServerMemberLeftEvent) -> None:
        try:
            await self.__permission_manager.remove_all_permissions(event.server_id, event.user_id)
            self.__logger.trace(
                "Removed moderation permissions of a user",
                server_id=event.server_id,
                user_id=event.user_id
            )
        except Exception as error:
            self.__logger.trace(
                "Failed to remove moderation permissions of a user",
                server_id=event.server_id,
                user_id=event.user_id,
                exception=error
            )
            await self.__try_log(
                event.server_id,
                (
                    f":exclamation: Failed to remove <@{event.user_id}>'s moderation permissions."
                    " A user with the required permission will have to do it manually."
                    " Either this was caused by an internal error or I don't have the required permissions."
                )
            )
            return

        await self.__try_log(
            event.server_id,
            f":hammer: <@{event.user_id}> has had their moderation permissions removed."
        )

    async def __try_log(self, server_id: str, message: str) -> None:
        try:
            await self.__log_manager.publish_log_entry(server_id, message)
        except (ChannelNotFoundError, ForbiddenError) as error:
            self.__logger.trace(
                "Failed to log a moderation log entry",
                server_id=server_id,
                entry=message,
                exception=error
            )
