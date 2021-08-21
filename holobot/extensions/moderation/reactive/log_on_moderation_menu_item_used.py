from ..context_menus import ModerationMenuItemBase
from ..context_menus.responses import (
    UserBannedResponse, UserKickedResponse, UserMutedResponse,
    UserUnmutedResponse, UserWarnedResponse
)
from ..managers import ILogManager
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError
from holobot.discord.sdk.events import MenuItemExecutedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from typing import Optional

@injectable(ListenerInterface[MenuItemExecutedEvent])
class LogOnModerationMenuItemUsed(ListenerInterface[MenuItemExecutedEvent]):
    def __init__(self, log: LogInterface, log_manager: ILogManager) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "LogOnModerationMenuItemUsed")
        self.__log_manager: ILogManager = log_manager

    async def on_event(self, event: MenuItemExecutedEvent):
        if (not issubclass(event.menu_item_type, ModerationMenuItemBase)
            or not (event_message := LogOnModerationMenuItemUsed.__create_event_message(event))):
            return
        
        try:
            is_published = await self.__log_manager.publish_log_entry(event.server_id, event_message)
            if not is_published:
                return
        except (ChannelNotFoundError, ForbiddenError):
            # TODO Notify the administrator.
            return

        self.__log.trace(f"A loggable moderation menu item has been used. {{ Type = {event.menu_item_type}, UserId = {event.user_id}, ServerId = {event.server_id} }}")

    @staticmethod
    def __create_event_message(event: MenuItemExecutedEvent) -> Optional[str]:
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
