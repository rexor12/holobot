from holobot.discord.sdk.models import Embed, EmbedFooter
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.utils import get_user_id
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.providers import IReactionProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError, RateLimitedError

_CATEGORIES = set((
    "awoo", "bite", "blush", "bonk", "bully", "cry", "cuddle", "dance",
    "handhold", "happy", "highfive", "hug", "kill", "kiss", "lick", "neko",
    "nom", "pat", "poke", "slap", "smile", "smug", "waifu", "wave", "wink"
))

@injectable(IWorkflow)
class ReactWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        member_data_provider: IMemberDataProvider,
        reaction_provider: IReactionProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__member_data_provider = member_data_provider
        self.__reaction_provider = reaction_provider

    @command(
        name="react",
        description="Shows a reaction with an animated picture.",
        options=(
            Option(name="action", description="The type of the reaction.", choices=tuple(
                Choice(name=category, value=category)
                for category in sorted(_CATEGORIES)
            )),
            Option(name="target", description="The name or mention of the target user.", is_mandatory=False)
        ),
        cooldown=Cooldown(duration=10)
    )
    async def show_reaction(
        self,
        context: ServerChatInteractionContext,
        action: str,
        target: str | None = None
    ) -> InteractionResponse:
        action = action.strip().lower()
        if action not in _CATEGORIES:
            return self._reply(content=self.__i18n_provider.get(
                "extensions.general.react_workflow.invalid_action_error"
            ))

        try:
            url = await self.__reaction_provider.get(action)
        except (CircuitBrokenError, HttpStatusError, TooManyRequestsError, RateLimitedError):
            return self._reply(content=self.__i18n_provider.get(
                "extensions.general.react_workflow.remote_api_error"
            ))

        if not url:
            return self._reply(content=self.__i18n_provider.get(
                "extensions.general.react_workflow.no_image_error"
            ))

        target_user_id = target and get_user_id(target)
        if target and not target_user_id:
            user_data = await self.__member_data_provider.get_basic_data_by_name(
                context.server_id,
                target
            )
            target_user_id = user_data.user_id
        if target_user_id == context.author_id:
            target_user_id = None

        return self._reply(
            content=Embed(
                title=self.__i18n_provider.get(
                    "extensions.general.react_workflow.embed_title",
                    { "user": context.author_display_name }
                ),
                description=self.__i18n_provider.get(
                    f"extensions.general.react_workflow.actions.{action}_target"
                    if target_user_id
                    else f"extensions.general.react_workflow.actions.{action}",
                    { "user_id": context.author_id, "target_user_id": target_user_id }
                ),
                image_url=url,
                footer=EmbedFooter(
                    text=self.__i18n_provider.get(
                        "extensions.general.react_workflow.embed_footer"
                    )
                )
            )
        )
