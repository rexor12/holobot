from .. import IMusicPlayer
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, ServerChatInteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class SkipSongCommand(CommandBase):
    def __init__(self, member_data_provider: IMemberDataProvider, music_player: IMusicPlayer) -> None:
        super().__init__("skip")
        self.group_name = "music"
        self.description = "Skips the currenlty playing song."
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__music_player: IMusicPlayer = music_player

    async def execute(self, context: ServerChatInteractionContext) -> CommandResponse:
        voice_channel_id = self.__member_data_provider.get_member_voice_channel_id(context.server_id, context.author_id)
        if not voice_channel_id:
            return CommandResponse(action=ReplyAction(content="You're not connected to my voice channel."))
        bot_channel_id = await self.__music_player.get_channel_id(context.server_id)
        if not bot_channel_id:
            return CommandResponse(action=ReplyAction(content="I'm not connected to a voice channel."))
        if bot_channel_id != voice_channel_id:
            return CommandResponse(action=ReplyAction(content="You aren't allowed to control the music player from another voice channel."))

        try:
            await self.__music_player.skip_song(context.server_id)
            return CommandResponse(action=ReplyAction(content="I've skipped the currently playing song."))
        except InvalidOperationError:
            return CommandResponse(action=ReplyAction(content="I'm not connected to a voice channel."))
