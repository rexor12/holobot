from .. import IMusicPlayer
from ..models import Song
from datetime import timedelta
from holobot.discord.sdk.models import Embed, EmbedField
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import textify_timedelta_short

@injectable(CommandInterface)
class GetPlayingSongCommand(CommandBase):
    def __init__(self, music_player: IMusicPlayer) -> None:
        super().__init__("current")
        self.group_name = "music"
        self.description = "Displays the currently playing song."
        self.__music_player: IMusicPlayer = music_player

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        bot_channel_id = await self.__music_player.get_channel_id(context.server_id)
        if not bot_channel_id:
            return CommandResponse(action=ReplyAction(content="I'm not connected to a voice channel."))
        current_song = await self.__music_player.get_currently_playing_song(context.server_id)
        if not current_song:
            return CommandResponse(action=ReplyAction(content="I'm not playing any songs right now."))

        embed = Embed(
            "Currently playing song",
            fields=[
                EmbedField(
                    name="Title",
                    value=current_song.audio_source.title,
                    is_inline=False
                )
            ]
        )
        
        self.__try_add_duration(current_song, embed)
        embed.fields.append(EmbedField(name="Requested by", value=f"<@!{current_song.queueing_user_id}>", is_inline=False))

        return CommandResponse(action=ReplyAction(content=embed))
    
    def __try_add_duration(self, song: Song, embed: Embed) -> None:
        if song.audio_source.duration is None:
            return
        
        progress_percentage = (song.audio_source.played_milliseconds / 1000.0) / song.audio_source.duration.seconds
        progress = timedelta(seconds=song.audio_source.duration.seconds * progress_percentage)
        progress_bar_count = int(progress_percentage * 10)
        progress_bar = (
            "<:progressleft:913113070547660810>"
            "" + ("<:progresscenter:913113070396637234>" * progress_bar_count) + ""
            "" + ("<:progresscenterempty:913119489929932831>" * (9 - progress_bar_count)) + ""
            "<:progressrightempty:913119512520445993>"
        )
        embed.fields.append(EmbedField(
            name="Progress",
            value=f"{textify_timedelta_short(progress)} {progress_bar} {textify_timedelta_short(song.audio_source.duration)}",
            is_inline=False
        ))
