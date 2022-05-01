from .. import IMusicPlayer
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import Choice, CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.sdk.exceptions import InvalidOperationError
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class StopPlaybackCommand(CommandBase):
    def __init__(self, member_data_provider: IMemberDataProvider, music_player: IMusicPlayer) -> None:
        super().__init__("stop")
        self.group_name = "music"
        self.description = "Stops playing songs."
        self.options = [
            Option("clear", "Whether or not to clear the list of songs. By default, songs are kept.", type=OptionType.INTEGER, is_mandatory=False, choices=[
                Choice("Yes", 1),
                Choice("No", 0)
            ]),
            Option("leave", "Whether or not to make the bot leave the channel. By default, the bot stays.", type=OptionType.INTEGER, is_mandatory=False, choices=[
                Choice("Yes", 1),
                Choice("No", 0)
            ])
        ]
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__music_player: IMusicPlayer = music_player

    async def execute(self, context: ServerChatInteractionContext, clear: int = 0, leave: int = 0) -> CommandResponse:
        voice_channel_id = self.__member_data_provider.get_member_voice_channel_id(context.server_id, context.author_id)
        if not voice_channel_id:
            return CommandResponse(action=ReplyAction(content="You're not connected to my voice channel."))
        bot_channel_id = await self.__music_player.get_channel_id(context.server_id)
        if not bot_channel_id:
            return CommandResponse(action=ReplyAction(content="I'm not connected to a voice channel."))
        if bot_channel_id != voice_channel_id:
            return CommandResponse(action=ReplyAction(content="You aren't allowed to control the music player from another voice channel."))

        try:
            await self.__music_player.stop_playback(context.server_id, clear != 0, leave != 0)
            return CommandResponse(action=ReplyAction(content="I've stopped playing music."))
        except InvalidOperationError:
            return CommandResponse(action=ReplyAction(content="I'm not playing any songs right now."))
