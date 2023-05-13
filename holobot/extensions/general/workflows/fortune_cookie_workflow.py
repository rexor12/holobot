from holobot.discord.sdk.models import Embed, EmbedFooter, InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Cooldown, InteractionResponse
from holobot.extensions.general.models import GeneralOptions
from holobot.extensions.general.repositories import IFortuneCookieRepository
from holobot.sdk.configs import IOptions
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable

@injectable(IWorkflow)
class FortuneCookieWorkflow(WorkflowBase):
    def __init__(
        self,
        fortune_cookie_repository: IFortuneCookieRepository,
        i18n_provider: II18nProvider,
        options: IOptions[GeneralOptions]
    ) -> None:
        super().__init__()
        self.__fortune_cookie_repository = fortune_cookie_repository
        self.__i18n_provider = i18n_provider
        self.__options = options

    @command(
        description="Crack open a cookie for good fortune.",
        name="cookie",
        cooldown=Cooldown(duration=30)
    )
    async def open_fortune_cookie(
        self,
        context: InteractionContext
    ) -> InteractionResponse:
        fortune_cookie = await self.__fortune_cookie_repository.get_random()
        if not fortune_cookie:
            return self._reply(
                content=self.__i18n_provider.get(
                    "extensions.general.fortune_cookie_workflow.no_cookies_error"
                )
            )

        return self._reply(
            embed=Embed(
                title=self.__i18n_provider.get("extensions.general.fortune_cookie_workflow.embed_title"),
                description=fortune_cookie.message,
                color=0xF9AE58,
                thumbnail_url=self.__options.value.FortuneCookieEmbedThumbnailUrl,
                footer=EmbedFooter(
                    text=self.__i18n_provider.get(
                        "extensions.general.fortune_cookie_workflow.embed_footer",
                        { "id": fortune_cookie.identifier }
                    )
                )
            )
        )
