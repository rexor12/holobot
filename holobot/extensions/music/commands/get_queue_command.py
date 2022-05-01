from .. import IMusicPlayer
from holobot.discord.sdk import IMessaging
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.components import Pager
from holobot.discord.sdk.models import Embed, EmbedField, EmbedFooter
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import textify_timedelta_short
from typing import Optional

@injectable(CommandInterface)
class GetQueueCommand(CommandBase):
    def __init__(self, log: LogInterface, messaging: IMessaging, music_player: IMusicPlayer) -> None:
        super().__init__("queue")
        self.group_name = "music"
        self.description = "Displays a paged list of the queued songs."
        self.options = [
            Option("page", "The starting page to display. By default, it's the first page.", OptionType.INTEGER, is_mandatory=False)
        ]
        self.__log: LogInterface = log.with_name("Music", "GetQueueCommand")
        self.__messaging: IMessaging = messaging
        self.__music_player: IMusicPlayer = music_player

    async def execute(self, context: ServerChatInteractionContext, page: int = 1) -> CommandResponse:
        if page < 1:
            page = 1
        
        bot_channel_id = await self.__music_player.get_channel_id(context.server_id)
        if not bot_channel_id:
            return CommandResponse(action=ReplyAction(content="I'm not connected to a voice channel."))

        await Pager(self.__messaging, self.__log, context, self.__create_embed, page - 1)
        return CommandResponse()
    
    async def __create_embed(self, context: ServerChatInteractionContext, page: int, page_size: int) -> Optional[Embed]:
        songs = await self.__music_player.get_queued_songs(context.server_id, page, page_size)
        if len(songs.results) == 0:
            return None
        
        embed = Embed(
            title="Songs in the queue",
            description=f"There are {songs.total_results} songs waiting to be played.",
            footer=EmbedFooter(
                text=f"Page {songs.page_index + 1}/{songs.page_count}"
            )
        )
        
        for index in range(len(songs.results)):
            song = songs.results[index]
            embed.fields.append(EmbedField(
                name=f"#{page * page_size + index + 1} {song.audio_source.title}",
                value=f"{textify_timedelta_short(song.audio_source.duration)} | Requested by <@!{song.queueing_user_id}>",
                is_inline=False
            ))
        
        return embed
