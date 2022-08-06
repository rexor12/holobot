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

    async def on_event(self, event: ServerMemberLeftEvent) -> None:
        await self.__permission_manager.remove_all_permissions(event.server_id, event.user_id)

        self.__logger.trace(
            "Removed moderation permissions of a user",
            server_id=event.server_id,
            user_id=event.user_id
        )

        try:
            await self.__log_manager.publish_log_entry(
                event.server_id,
                f":hammer: <@{event.user_id}> has had their moderation permissions removed."
            )
        except (ChannelNotFoundError, ForbiddenError):
            # TODO Notify the administrator.
            return
