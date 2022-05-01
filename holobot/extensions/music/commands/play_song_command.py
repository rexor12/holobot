from .song_player_command_base import SongPlayerCommandBase
from .. import IMusicPlayer
from ..enums import QueueMode
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import Choice, CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface

import re

URL_REGEX = re.compile(r"^https?\:\/{2}.*$", re.IGNORECASE)

@injectable(CommandInterface)
class PlaySongCommand(SongPlayerCommandBase):
    def __init__(self, member_data_provider: IMemberDataProvider, music_player: IMusicPlayer, log: LogInterface) -> None:
        super().__init__("play", member_data_provider, music_player, log.with_name("Music", "PlaySongCommand"))
        self.group_name = "music"
        self.description = "Plays a specific song."
        self.options = [
            Option("song", "The title or URL of the song to play.", is_mandatory=True),
            Option("mode", "Determines how the song is to be queued. Default is the end of the queue.", OptionType.INTEGER, is_mandatory=False, choices=[
                Choice("End of queue", 0),
                Choice("As next one", 1),
                Choice("Skip current one", 2)
            ])
        ]

    async def execute(self, context: ServerChatInteractionContext, song: str, mode: int = 0) -> CommandResponse:
        if (error_message := await self._try_join_voice_channel(context)):
            return CommandResponse(action=ReplyAction(content=error_message))

        if URL_REGEX.match(song) is None:
            song_metadatas = await self._music_player.search_songs(song, 1)
            if len(song_metadatas) == 0:
                return CommandResponse(action=ReplyAction(content="I can't find the song you're looking for."))
            else: song = song_metadatas[0].url

        return CommandResponse(action=ReplyAction(
            content=await self._enqueue_song(context, song, QueueMode.parse(mode))
        ))
