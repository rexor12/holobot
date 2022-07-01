from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class ViewEmojiCommand(CommandBase):
    def __init__(self, emoji_data_provider: IEmojiDataProvider) -> None:
        super().__init__("emoji")
        self.__emoji_data_provider: IEmojiDataProvider = emoji_data_provider
        self.description = "Displays an emoji in a larger size."
        self.options = [
            Option("name", "The name of or the emoji itself.")
        ]

    async def execute(self, context: ServerChatInteractionContext, name: str) -> CommandResponse:
        if (emoji := await self.__emoji_data_provider.find_emoji(name.strip())) is None:
            return CommandResponse(
                action=ReplyAction(content="The specified emoji cannot be found. Did you make a typo?")
            )

        if not emoji.url:
            return CommandResponse(ReplyAction((
                "The specified emoji isn't a custom emoji, therefore it has no attributes."
            )))

        return CommandResponse(
            action=ReplyAction(content=emoji.url)
        )
