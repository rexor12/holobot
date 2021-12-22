from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.data_providers import IBotDataProvider
from holobot.discord.sdk.models import Embed, EmbedFooter
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.sdk.configs import ConfiguratorInterface
from holobot.sdk.ioc.decorators import injectable
from typing import Optional

@injectable(CommandInterface)
class ViewUserAvatarCommand(CommandBase):
    def __init__(self,
                 configurator: ConfiguratorInterface,
                 bot_data_provider: IBotDataProvider,
                 member_data_provider: IMemberDataProvider) -> None:
        super().__init__("avatar")
        self.description = "Displays a user's avatar."
        self.options = [
            Option("user", "The name or mention of the user. By default, it's yourself.", is_mandatory=False)
        ]
        self.__bot_data_provider: IBotDataProvider = bot_data_provider
        self.__member_data_provider: IMemberDataProvider = member_data_provider
        self.__avatar_artwork_artist_name: str = configurator.get("General", "AvatarArtworkArtistName", "unknown")

    async def execute(self, context: ServerChatInteractionContext, user: Optional[str] = None) -> CommandResponse:
        try:
            if user is None:
                member = self.__member_data_provider.get_basic_data_by_id(context.server_id, context.author_id)
            elif (user_id := get_user_id(user)) is not None:
                member = self.__member_data_provider.get_basic_data_by_id(context.server_id, user_id)
            else:
                member = self.__member_data_provider.get_basic_data_by_name(context.server_id, user.strip())
        except:
            # TODO guild/user not found
            return CommandResponse(
                action=ReplyAction(content="The specified user cannot be found. Did you make a typo?")
            )

        if member.user_id == self.__bot_data_provider.get_user_id():
            footer = EmbedFooter(text=f"Artwork by {self.__avatar_artwork_artist_name}")
        else: footer = None
        
        return CommandResponse(
            action=ReplyAction(content=Embed(
                title=f"{member.display_name}'s avatar",
                image_url=member.avatar_url,
                footer=footer
            ))
        )
