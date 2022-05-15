from .ibot_event_handler import IBotEventHandler
from discord import StageChannel, VoiceChannel, VoiceState
from discord_slash import SlashContext
from holobot.discord.sdk.audio.events import UserJoinedAudioChannelEvent, UserLeftAudioChannelEvent
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.reactive import ListenerInterface
from typing import Optional, Tuple, Union

import discord.ext.commands as commands

@injectable(IBotEventHandler)
class BotEventHandler(IBotEventHandler):
    def __init__(self,
                 log: LogInterface,
                 user_joined_audio_channel_event_listeners: Tuple[ListenerInterface[UserJoinedAudioChannelEvent], ...],
                 user_left_audio_channel_event_listeners: Tuple[ListenerInterface[UserLeftAudioChannelEvent], ...]) -> None:
        super().__init__()
        self.__log: LogInterface = log.with_name("Discord", "BotEventHandler")
        self.__user_joined_audio_channel_event_listeners: Tuple[ListenerInterface[UserJoinedAudioChannelEvent], ...] = user_joined_audio_channel_event_listeners
        self.__user_left_audio_channel_event_listeners: Tuple[ListenerInterface[UserLeftAudioChannelEvent], ...] = user_left_audio_channel_event_listeners

    def register_callbacks(self, bot: commands.Bot) -> None:
        bot.add_listener(self.__on_slash_command_error, "on_slash_command_error")
        bot.add_listener(self.__on_voice_state_update, "on_voice_state_update")

    async def __on_slash_command_error(self, context: SlashContext, exception: Exception) -> None:
        self.__log.error((
            "An error has occurred while processing a slash command. "
            f"{{ Type = {type(exception).__name__}, UserId = {context.author_id} }}"
            ), exception)

    async def __on_voice_state_update(self, member, before: VoiceState, after: VoiceState) -> None:
        previous_channel: Optional[Union[VoiceChannel, StageChannel]] = before.channel if before else None
        current_channel: Optional[Union[VoiceChannel, StageChannel]] = after.channel if after else None

        if previous_channel and (not current_channel or previous_channel.id != current_channel.id):
            for listener in self.__user_left_audio_channel_event_listeners:
                await listener.on_event(UserLeftAudioChannelEvent(
                    server_id=str(previous_channel.guild.id),
                    channel_id=str(previous_channel.id),
                    user_id=str(member.id)
                ))

        if current_channel and (not previous_channel or previous_channel.id != current_channel.id):
            for listener in self.__user_joined_audio_channel_event_listeners:
                await listener.on_event(UserJoinedAudioChannelEvent(
                    server_id=str(current_channel.guild.id),
                    channel_id=str(current_channel.id),
                    user_id=str(member.id)
                ))
