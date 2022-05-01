from .song_player_command_base import SongPlayerCommandBase
from .. import IMusicPlayer
from ..enums import QueueMode
from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import Choice, CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.components import ComboBox, ComboBoxItem
from holobot.discord.sdk.components.models import ComboBoxState, ComponentInteractionResponse, ComponentRegistration
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.logging import LogInterface
from holobot.sdk.utils import textify_timedelta_short

@injectable(CommandInterface)
class SearchSongCommand(SongPlayerCommandBase):
    def __init__(self, member_data_provider: IMemberDataProvider, music_player: IMusicPlayer, log: LogInterface) -> None:
        super().__init__("search", member_data_provider, music_player, log.with_name("Music", "SearchSongCommand"))
        self.group_name = "music"
        self.description = "Searches for matching songs and plays the selection."
        self.options = [
            Option("title", "The title of the song to play.", is_mandatory=True),
            Option("mode", "Determines how the song is to be queued. Default is the end of the queue.", OptionType.INTEGER, is_mandatory=False, choices=[
                Choice("End of queue", 0),
                Choice("As next one", 1),
                Choice("Skip current one", 2)
            ])
        ]
        self.components = [
            ComponentRegistration("search_song_selector", ComboBox, self.__on_song_selected)
        ]

    async def execute(self, context: ServerChatInteractionContext, title: str, mode: int = 0) -> CommandResponse:
        if (error_message := await self._try_join_voice_channel(context)):
            return CommandResponse(action=ReplyAction(content=error_message))

        song_metadatas = await self._music_player.search_songs(title)
        if len(song_metadatas) == 0:
            return CommandResponse(action=ReplyAction(content="I can't find the song you're looking for."))
        else: return CommandResponse(action=ReplyAction(content="Choose the song you'd like me to play.", components=ComboBox(
            id="search_song_selector",
            items=[ComboBoxItem(
                text=f"{metadata.title} ({textify_timedelta_short(metadata.duration)})"[0:80],
                value=f"{mode};{metadata.url}"[0:100]
            ) for metadata in song_metadatas]
        )))

    async def __on_song_selected(self, registration: ComponentRegistration, context: InteractionContext, state: ComboBoxState) -> ComponentInteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return ComponentInteractionResponse(action=ReplyAction(content="I'm sorry, this command is available in servers only."))

        if len(state.selected_values) == 0:
            return ComponentInteractionResponse(action=ReplyAction(content="You must select a value from the combo box."))

        if (error_message := await self._try_join_voice_channel(context)):
            return ComponentInteractionResponse(action=ReplyAction(content=error_message))

        mode, url = state.selected_values[0].split(";", 1)
        return ComponentInteractionResponse(action=ReplyAction(
            content=await self._enqueue_song(context, url, QueueMode.parse(int(mode)))
        ))
