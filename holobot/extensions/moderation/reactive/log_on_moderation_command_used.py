from ..commands import ModerationCommandBase
from ..commands.responses import (
    LogChannelToggledResponse, ModeratorPermissionsChangedResponse,
    UserBannedResponse, UserKickedResponse, UserMutedResponse, UserUnmutedResponse,
    UserWarnedResponse, WarnDecayToggledResponse
)
from ..repositories import ILogSettingsRepository
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.events import CommandExecutedEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from holobot.sdk.utils import textify_timedelta
from typing import Optional

@injectable(ListenerInterface[CommandExecutedEvent])
class LogOnModerationCommandUsed(ListenerInterface[CommandExecutedEvent]):
    def __init__(self, log: LogInterface, log_settings_repository: ILogSettingsRepository, messaging: IMessaging) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Moderation", "LogOnModerationCommandUsed")
        self.__log_settings_repository: ILogSettingsRepository = log_settings_repository
        self.__messaging: IMessaging = messaging

    async def on_event(self, event: CommandExecutedEvent):
        if (not issubclass(event.command_type, ModerationCommandBase)
            or not (event_message := LogOnModerationCommandUsed.__create_event_message(event))):
            return
        
        log_channel = await self.__log_settings_repository.get_log_channel(event.server_id)
        if not log_channel:
            return

        self.__log.trace(f"A moderation command has been used. {{ Name = {event.command}, UserId = {event.user_id}, ServerId = {event.server_id} }}")
        await self.__messaging.send_guild_message(log_channel, event_message)
    
    @staticmethod
    def __create_event_message(event: CommandExecutedEvent) -> Optional[str]:
        response = event.response
        if isinstance(response, UserWarnedResponse):
            return f":warning: <@{response.author_id}> has warned <@{response.user_id}> with the reason '{response.reason}'."
        if isinstance(response, UserMutedResponse): # TODO Add duration.
            return f":mute: <@{response.author_id}> has muted <@{response.user_id}> with the reason '{response.reason}'."
        if isinstance(response, UserUnmutedResponse):
            return f":loud_sound: <@{response.author_id}> has unmuted <@{response.user_id}>."
        if isinstance(response, UserBannedResponse):
            return f":no_entry_sign: <@{response.author_id}> has banned <@{response.user_id}> with the reason '{response.reason}'."
        if isinstance(response, UserKickedResponse):
            return f"<@{response.author_id}> has kicked <@{response.user_id}> with the reason '{response.reason}'."
        if isinstance(response, ModeratorPermissionsChangedResponse):
            if response.is_addition:
                return f":shield: <@{response.author_id}> has granted <@{response.user_id}> the permission to {response.permission.textify()}."
            else: return f":shield: <@{response.author_id}> has revoked <@{response.user_id}>'s permission to {response.permission.textify()}."
        if isinstance(response, LogChannelToggledResponse):
            if response.is_enabled:
                return f":clipboard: <@{response.author_id}> has enabled moderation command logging in <#{response.channel_id}>."
            else: return f":clipboard: <@{response.author_id}> has disabled moderation command logging."
        if isinstance(response, WarnDecayToggledResponse):
            if response.is_enabled:
                return f":gear: <@{response.author_id}> has enabled automatic warn strike removal after {textify_timedelta(response.duration)}."
            else: return f":gear: <@{response.author_id}> has disabled automatic warn strike removal."
        return None
