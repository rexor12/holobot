from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ViewEmojiWorkflow(WorkflowBase):
    def __init__(self, emoji_data_provider: IEmojiDataProvider) -> None:
        super().__init__()
        self.__emoji_data_provider: IEmojiDataProvider = emoji_data_provider

    @command(
        description="Displays an emoji in a larger size.",
        name="emoji",
        options=(
            Option("name", "The name of or the emoji itself."),
        )
    )
    async def show_emoji(
        self,
        context: ServerChatInteractionContext,
        name: str
    ) -> InteractionResponse:
        if (emoji := await self.__emoji_data_provider.find_emoji(name.strip())) is None:
            return InteractionResponse(
                action=ReplyAction(content="The specified emoji cannot be found. Did you make a typo?")
            )

        if not emoji.url:
            return InteractionResponse(ReplyAction((
                "The specified emoji isn't a custom emoji, therefore it has no attributes."
            )))

        return InteractionResponse(
            action=ReplyAction(content=emoji.url)
        )
