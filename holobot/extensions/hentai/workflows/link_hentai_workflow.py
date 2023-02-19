import re

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.models import InteractionContext
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.sdk.i18n import II18nProvider
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import try_parse_int

NHENTAI_SITE_ID = "nhentai"
EHENTAI_SITE_ID = "ehentai"

ehentai_regex = re.compile(r"^(?:\d+)\/(?:[a-z0-9]{10})$")

@injectable(IWorkflow)
class LinkHentaiWorkflow(WorkflowBase):
    def __init__(
        self,
        i18n_provider: II18nProvider
    ) -> None:
        super().__init__()
        self.__i18n_provider = i18n_provider

    @command(
        description="Gives you a link to a title on a specific site.",
        name="link",
        group_name="hentai",
        options=(
            Option("site", "The name of the site.", choices=(
                Choice("nhentai", NHENTAI_SITE_ID),
                Choice("e-hentai", EHENTAI_SITE_ID)
            )),
            Option("code", "The identifier of the title.")
        )
    )
    async def show_hentai_link(
        self,
        context: InteractionContext,
        site: str,
        code: str
    ) -> InteractionResponse:
        if not site or not code:
            return InteractionResponse(
                action=ReplyAction(content=self.__i18n_provider.get(
                    "extensions.hentai.link_hentai_workflow.missing_site_or_code_error"
                ))
            )
        code = code.strip()
        if site == NHENTAI_SITE_ID:
            if (value := try_parse_int(code)) is None:
                return InteractionResponse(
                    action=ReplyAction(content=self.__i18n_provider.get(
                        "extensions.hentai.link_hentai_workflow.nhentai_invalid_code_error"
                    ))
                )
            return InteractionResponse(
                action=ReplyAction(content=f"https://nhentai.net/g/{value}")
            )
        elif site == EHENTAI_SITE_ID:
            return InteractionResponse(action=ReplyAction(
                content=f"https://e-hentai.org/g/{code}"
                if ehentai_regex.match(code)
                else self.__i18n_provider.get(
                    "extensions.hentai.link_hentai_workflow.ehentai_invalid_code_error"
                )
            ))

        return InteractionResponse(
            action=ReplyAction(content=self.__i18n_provider.get(
                "extensions.hentai.link_hentai_workflow.invalid_site_error"
            ))
        )
