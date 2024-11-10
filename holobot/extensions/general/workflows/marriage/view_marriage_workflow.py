from holobot.discord.sdk.models import Embed, EmbedField, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.enums import OptionType
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.extensions.general.managers import IMarriageManager
from holobot.extensions.general.options import GeneralOptions
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class ViewMarriageWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider,
        marriage_manager: IMarriageManager,
        options: IOptions[GeneralOptions]
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider
        self.__marriage_manager = marriage_manager
        self.__options = options

    @command(
        group_name="marriage",
        name="view",
        description="Shows information about your or another user's marriage.",
        options=(
            Option("user", "The user whose marriage you want to see.", OptionType.USER, False),
        ),
        cooldown=Cooldown(duration=10)
    )
    async def view_marriage(
        self,
        context: InteractionContext,
        user: int | None = None
    ) -> InteractionResponse:
        if not isinstance(context, ServerChatInteractionContext):
            return self._reply(
                content=self.__i18n_provider.get("interactions.server_only_interaction_error")
            )

        user_id = user if user else context.author_id
        marriage = await self.__marriage_manager.get_marriage(context.server_id, user_id)
        if not marriage:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.general.view_marriage_workflow.other_not_married_error"
                    if user
                    else "extensions.general.view_marriage_workflow.not_married_error",
                    { "user_id": user_id }
                ),
                suppress_user_mentions=True
            )

        if marriage.level - 1 >= len(self.__options.value.MarriageActivityExpTable):
            exp_value = self.__i18n_provider.get(
                "extensions.general.view_marriage_workflow.xp_max_value"
            )
        else:
            exp_value = self.__i18n_provider.get(
                "extensions.general.view_marriage_workflow.xp_value",
                {
                    "current_xp": marriage.exp_points,
                    "required_xp": self.__options.value.MarriageActivityExpTable[marriage.level - 1]
                }
            )

        return self._reply(
            embed=Embed(
                title=self.__i18n_provider.get(
                    "extensions.general.view_marriage_workflow.embed_title"
                ),
                description=self.__i18n_provider.get(
                    "extensions.general.view_marriage_workflow.embed_description",
                    {
                        "user_id1": marriage.user_id1,
                        "user_id2": marriage.user_id2,
                        "married_at": int(marriage.married_at.timestamp()),
                        "hugs": marriage.hug_count,
                        "kisses": marriage.kiss_count,
                        "pats": marriage.pat_count,
                        "pokes": marriage.poke_count,
                        "licks": marriage.lick_count,
                        "bites": marriage.bite_count,
                        "handholds": marriage.handhold_count,
                        "cuddles": marriage.cuddle_count
                    }
                ),
                color=0xFF007F,
                thumbnail_url=self.__options.value.MarriageEmbedThumbnailUrl or None,
                fields=[
                    EmbedField(
                        self.__i18n_provider.get(
                            "extensions.general.view_marriage_workflow.embed_field_level"
                        ),
                        str(marriage.level)
                    ),
                    EmbedField(
                        self.__i18n_provider.get(
                            "extensions.general.view_marriage_workflow.embed_field_xp"
                        ),
                        exp_value
                    ),
                    EmbedField(
                        self.__i18n_provider.get(
                            "extensions.general.view_marriage_workflow.embed_field_match_bonus"
                        ),
                        f"+{marriage.match_bonus * 100}%"
                    )
                ]
            )
        )
