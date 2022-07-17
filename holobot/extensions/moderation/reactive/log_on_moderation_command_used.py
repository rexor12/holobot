from ..managers import ILogManager
from ..workflows.interactables import ModerationCommand
from ..workflows.responses import (
    AutoBanToggledResponse, AutoKickToggledResponse, AutoMuteToggledResponse,
    LogChannelToggledResponse, ModeratorPermissionsChangedResponse,
    UserBannedResponse, UserKickedResponse, UserMutedResponse, UserUnmutedResponse,
    UserWarnedResponse, WarnDecayToggledResponse
)
from holobot.discord.sdk.exceptions import ChannelNotFoundError, ForbiddenError
from holobot.discord.sdk.events import CommandExecutedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from holobot.sdk.utils import textify_timedelta
from typing import Optional

@injectable(ListenerInterface[CommandExecutedEvent])
class LogOnModerationCommandUsed(ListenerInterface[CommandExecutedEvent]):
    def __init__(self, log: LogInterface, log_manager: ILogManager) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "LogOnModerationCommandUsed")
        self.__log_manager: ILogManager = log_manager

    async def on_event(self, event: CommandExecutedEvent):
        if (not issubclass(event.command_type, ModerationCommand)
            or not (event_message := LogOnModerationCommandUsed.__create_event_message(event))):
            return
        
        try:
            is_published = await self.__log_manager.publish_log_entry(event.server_id, event_message)
            if not is_published:
                return
        except (ChannelNotFoundError, ForbiddenError):
            # TODO Notify the administrator.
            return

        self.__log.trace(f"A loggable moderation command has been used. {{ Name = {event.command}, UserId = {event.user_id}, ServerId = {event.server_id} }}")

    @staticmethod
    def __create_event_message(event: CommandExecutedEvent) -> Optional[str]:
        response = event.response
        if isinstance(response, UserWarnedResponse):
            return f":warning: <@{response.author_id}> has warned <@{response.user_id}> with the reason '{response.reason}'."
        if isinstance(response, UserMutedResponse):
            duration = textify_timedelta(response.duration) if response.duration is not None else "an unspecified duration"
            return f":mute: <@{response.author_id}> has muted <@{response.user_id}> with the reason '{response.reason}' for {duration}."
        if isinstance(response, UserUnmutedResponse):
            return f":loud_sound: <@{response.author_id}> has unmuted <@{response.user_id}>."
        if isinstance(response, UserBannedResponse):
            return f":no_entry: <@{response.author_id}> has banned <@{response.user_id}> with the reason '{response.reason}'."
        if isinstance(response, UserKickedResponse):
            return f":x: <@{response.author_id}> has kicked <@{response.user_id}> with the reason '{response.reason}'."
        if isinstance(response, ModeratorPermissionsChangedResponse):
            if response.is_addition:
                return f":shield: <@{response.author_id}> has granted <@{response.user_id}> the permission to {response.permission.textify()}."
            return f":shield: <@{response.author_id}> has revoked <@{response.user_id}>'s permission to {response.permission.textify()}."
        if isinstance(response, LogChannelToggledResponse):
            if response.is_enabled:
                return f":clipboard: <@{response.author_id}> has enabled moderation command logging in <#{response.channel_id}>."
            return f":clipboard: <@{response.author_id}> has disabled moderation command logging."
        if isinstance(response, AutoBanToggledResponse):
            if response.is_enabled:
                return f":gear: <@{response.author_id}> has enabled the automatic banning of users after {response.warn_count} warn strikes."
            return f":gear: <@{response.author_id}> has disabled the automatic banning of users."
        if isinstance(response, AutoKickToggledResponse):
            if response.is_enabled:
                return f":gear: <@{response.author_id}> has enabled the automatic kicking of users after {response.warn_count} warn strikes."
            return f":gear: <@{response.author_id}> has disabled the automatic kicking of users."
        if isinstance(response, AutoMuteToggledResponse):
            if response.is_enabled:
                duration = textify_timedelta(response.duration) if response.duration is not None else "an unspecified duration"
                return f":gear: <@{response.author_id}> has enabled the automatic muting of users after {response.warn_count} warn strikes for {duration}."
            return f":gear: <@{response.author_id}> has disabled the automatic muting of users."
        if isinstance(response, WarnDecayToggledResponse):
            if response.is_enabled:
                return f":gear: <@{response.author_id}> has enabled automatic warn strike removal after {textify_timedelta(response.duration)}."
            return f":gear: <@{response.author_id}> has disabled automatic warn strike removal."
        return None
