from collections.abc import Awaitable

from holobot.discord.sdk.exceptions import (
    ChannelNotFoundError, ServerNotFoundError, UserNotFoundError
)
from holobot.discord.sdk.models import Embed, EmbedFooter, InteractionContext
from holobot.discord.sdk.servers import IMemberDataProvider
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables import Command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import (
    Choice, Cooldown, InteractionResponse, Option
)
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.enums import ReactionType
from holobot.extensions.general.providers import IReactionProvider
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.network.exceptions import HttpStatusError, TooManyRequestsError
from holobot.sdk.network.resilience.exceptions import CircuitBrokenError, RateLimitedError

_CATEGORY_NAMES_BY_TYPE: dict[ReactionType, str] = {
    ReactionType.AWOO: "awoo",
    ReactionType.BITE: "bite",
    ReactionType.BLUSH: "blush",
    ReactionType.BONK: "bonk",
    ReactionType.BULLY: "bully",
    ReactionType.CRY: "cry",
    ReactionType.CUDDLE: "cuddle",
    ReactionType.DANCE: "dance",
    ReactionType.HANDHOLD: "handhold",
    ReactionType.HAPPY: "happy",
    ReactionType.HIGHFIVE: "highfive",
    ReactionType.HUG: "hug",
    ReactionType.KILL: "kill",
    ReactionType.KISS: "kiss",
    ReactionType.LICK: "lick",
    ReactionType.NEKO: "neko",
    ReactionType.NOM: "nom",
    ReactionType.PAT: "pat",
    ReactionType.POKE: "poke",
    ReactionType.SLAP: "slap",
    ReactionType.SMILE: "smile",
    ReactionType.SMUG: "smug",
    ReactionType.WAIFU: "waifu",
    ReactionType.WAVE: "wave",
    ReactionType.WINK: "wink"
}

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
        self.__register_reactions()

    def __register_reactions(self) -> None:
        for reaction_type, reaction_name in _CATEGORY_NAMES_BY_TYPE.items():
            def callback_factory(rt: ReactionType):
                def show_reaction(
                    workflow: WorkflowBase,
                    context: InteractionContext,
                    target: int | None = None
                ) -> Awaitable[InteractionResponse]:
                    return self.__show_reaction(context, rt, target)

                return show_reaction

            self.add_registration(
                Command(
                    group_name="react",
                    name=reaction_name,
                    description="Shows a reaction with an animated picture.",
                    cooldown=Cooldown(
                        duration=10,
                        message="extensions.general.react_workflow.cooldown_error"
                    ),
                    options=(
                        Option("target", "The target user.", OptionType.USER, False),
                    ),
                    callback=callback_factory(reaction_type)
                )
            )

    async def __show_reaction(
        self,
        context: InteractionContext,
        reaction_type: ReactionType,
        target: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        if reaction_type not in _CATEGORY_NAMES_BY_TYPE:
            return self._reply(content=self.__i18n_provider.get(
                "extensions.general.react_workflow.invalid_action_error"
            ))

        reaction_name = _CATEGORY_NAMES_BY_TYPE[reaction_type]
        try:
            url = await self.__reaction_provider.get(reaction_name)
        except (CircuitBrokenError, HttpStatusError, TooManyRequestsError, RateLimitedError):
            return self._reply(content=self.__i18n_provider.get(
                "extensions.general.react_workflow.remote_api_error"
            ))

        if not url:
            return self._reply(content=self.__i18n_provider.get(
                "extensions.general.react_workflow.no_image_error"
            ))

        target_user_id = None
        if target:
            try:
                user_data = await self.__member_data_provider.get_basic_data_by_id(
                    context.server_id,
                    target
                )
                target_user_id = user_data.user_id
            except UserNotFoundError:
                return self._reply(content=self.__i18n_provider.get("user_not_found_error"))
            except ServerNotFoundError:
                return self._reply(content=self.__i18n_provider.get("server_not_found_error"))
            except ChannelNotFoundError:
                return self._reply(content=self.__i18n_provider.get("channel_not_found_error"))

        if target_user_id == context.author_id:
            target_user_id = None

        return self._reply(
            embed=Embed(
                title=self.__i18n_provider.get(
                    "extensions.general.react_workflow.embed_title",
                    { "user": context.author_display_name }
                ),
                description=self.__i18n_provider.get(
                    f"extensions.general.react_workflow.actions.{reaction_name}_target"
                    if target_user_id
                    else f"extensions.general.react_workflow.actions.{reaction_name}",
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
