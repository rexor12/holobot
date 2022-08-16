
from ..managers import ILogManager
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError
from holobot.discord.sdk.events import MenuItemProcessedEvent
from holobot.extensions.moderation.workflows.interactables import ModerationMenuItem
from holobot.extensions.moderation.workflows.responses.menu_item_responses import (
    UserBannedResponse, UserKickedResponse, UserMutedResponse,
    UserUnmutedResponse, UserWarnedResponse
)
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import ILoggerFactory
from holobot.sdk.reactive import IListener

@injectable(IListener[MenuItemProcessedEvent])
class LogOnModerationMenuItemUsed(IListener[MenuItemProcessedEvent]):
    def __init__(
        self,
        log_manager: ILogManager,
        logger_factory: ILoggerFactory
    ) -> None:
        super().__init__()
        self.__logger = logger_factory.create(LogOnModerationMenuItemUsed)
        self.__log_manager: ILogManager = log_manager

    async def on_event(self, event: MenuItemProcessedEvent):
        if (not event.server_id
            or not issubclass(event.menu_item_type, ModerationMenuItem)
            or not (event_message := LogOnModerationMenuItemUsed.__create_event_message(event))):
            return

        try:
            is_published = await self.__log_manager.publish_log_entry(event.server_id, event_message)
            if not is_published:
                return
        except (ChannelNotFoundError, ForbiddenError):
            # TODO Notify the administrator.
            return

        self.__logger.trace(
            "A loggable moderation menu item has been used",
            type=event.menu_item_type,
            user_id=event.user_id,
            server_id=event.server_id
        )

    @staticmethod
    def __create_event_message(event: MenuItemProcessedEvent) -> str | None:
        response = event.response
        if isinstance(response, UserWarnedResponse):
            return f":warning: <@{response.author_id}> has warned <@{response.user_id}> via a context menu item."
        if isinstance(response, UserMutedResponse):
            return f":mute: <@{response.author_id}> has muted <@{response.user_id}> via a context menu item for an unspecified duration."
        if isinstance(response, UserUnmutedResponse):
            return f":loud_sound: <@{response.author_id}> has unmuted <@{response.user_id}>."
        if isinstance(response, UserBannedResponse):
            return f":no_entry: <@{response.author_id}> has banned <@{response.user_id}> via a context menu item."
        if isinstance(response, UserKickedResponse):
            return f":x: <@{response.author_id}> has kicked <@{response.user_id}> via a context menu item."
        return None
