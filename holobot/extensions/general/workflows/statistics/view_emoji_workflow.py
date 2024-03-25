from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.data_providers import IEmojiDataProvider
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import InteractionResponse, Option
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ViewEmojiWorkflow(WorkflowBase):
    def __init__(
        self,
        emoji_data_provider: IEmojiDataProvider,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__emoji_data_provider: IEmojiDataProvider = emoji_data_provider
        self.__i18n_provider = i18n_provider

    @command(
        description="Displays an emoji in a larger size.",
        name="emoji",
        options=(
            Option("name", "The name of or the emoji itself."),
        )
    )
    async def show_emoji(
        self,
        context: InteractionContext,
        name: str
    ) -> InteractionResponse:
        if (emoji := await self.__emoji_data_provider.find_emoji(name.strip())) is None:
            return InteractionResponse(action=ReplyAction(content=self.__i18n_provider.get(
                "extensions.general.view_emoji_workflow.emoji_not_found_error"
            )))

        if not emoji.url:
            return InteractionResponse(ReplyAction(content=self.__i18n_provider.get(
                "extensions.general.view_emoji_workflow.invalid_emoji_error"
            )))

        return InteractionResponse(
            action=ReplyAction(content=emoji.url)
        )
