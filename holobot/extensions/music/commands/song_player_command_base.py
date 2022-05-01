from .. import IMusicPlayer
from ..enums import QueueMode
from ..models import Song
from holobot.discord.sdk.commands import CommandBase
from holobot.discord.sdk.commands.models import ServerChatInteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import textify_timedelta_short
from typing import Optional, Tuple

class SongPlayerCommandBase(CommandBase):
    def __init__(self, command_name: str, member_data_provider: IMemberDataProvider, music_player: IMusicPlayer, log: LogInterface) -> None:
        super().__init__(command_name)
        self._log: LogInterface = log
        self._member_data_provider: IMemberDataProvider = member_data_provider
        self._music_player: IMusicPlayer = music_player

    @staticmethod
    def __construct_response_text(queued_songs: Tuple[Song, ...]) -> str:
        if len(queued_songs) > 1:
            response_text = f"Queued {len(queued_songs)} songs."
        elif len(queued_songs) == 1:
            response_text_bits = ["Queued `", queued_songs[0].audio_source.title.replace("`", ""), "`"]
            if queued_songs[0].audio_source.duration is not None:
                response_text_bits.append(" (")
                response_text_bits.append(textify_timedelta_short(queued_songs[0].audio_source.duration))
                response_text_bits.append(")")
            response_text_bits.append(".")
            response_text = "".join(response_text_bits)
        else: response_text = "Failed to queue the song. It might be unavailable to me."
        return response_text

    async def _try_join_voice_channel(self, context: ServerChatInteractionContext) -> Optional[str]:
        voice_channel_id = self._member_data_provider.get_member_voice_channel_id(context.server_id, context.author_id)
        if not voice_channel_id:
            return "You're not connected to a voice channel."

        try:
            await self._music_player.join_channel(context.server_id, voice_channel_id, context.author_id)
            return None
        except InvalidOperationError:
            return "I'm already connected to another voice channel."

    async def _enqueue_song(self, context: ServerChatInteractionContext, url: str, mode: QueueMode) -> str:
        try:
            queued_songs = await self._music_player.queue_songs(context.server_id, context.author_id, url, mode)
        except InvalidOperationError:
            return "I'm not connected to your voice channel."
        except Exception as error:
            self._log.debug(f"Error while playing a song: {error}")
            return "An error occurred while loading the song. I might be geo-restricted or the song is private."

        return SongPlayerCommandBase.__construct_response_text(queued_songs)
