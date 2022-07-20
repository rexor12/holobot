import re

from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.workflows import IWorkflow, WorkflowBase
from holobot.discord.sdk.workflows.interactables.decorators import command
from holobot.discord.sdk.workflows.interactables.models import Choice, InteractionResponse, Option
from holobot.discord.sdk.workflows.models import ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import try_parse_int

NHENTAI_SITE_ID = "nhentai"
EHENTAI_SITE_ID = "ehentai"

ehentai_regex = re.compile(r"^(?:\d+)\/(?:[a-z0-9]{10})$")

@injectable(IWorkflow)
class LinkHentaiWorkflow(WorkflowBase):
    def __init__(self) -> None:
        super().__init__()

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
        context: ServerChatInteractionContext,
        site: str,
        code: str
    ) -> InteractionResponse:
        if not site or not code:
            return InteractionResponse(
                action=ReplyAction(content="You must specify both the site and the identifier.")
            )
        code = code.strip()
        if site == NHENTAI_SITE_ID:
            if (value := try_parse_int(code)) is None:
                return InteractionResponse(
                    action=ReplyAction(content="Invalid identifier. A valid identifier, for example, is _206981_.")
                )
            return InteractionResponse(
                action=ReplyAction(content=f"https://nhentai.net/g/{value}")
            )
        elif site == EHENTAI_SITE_ID:
            return InteractionResponse(action=ReplyAction(
                content=f"https://e-hentai.org/g/{code}"
                if ehentai_regex.match(code)
                else "Invalid identifier. A valid identifier, for example, is _1383239/0e7abac58a_ (case-sensitive)."
            ))

        return InteractionResponse(
            action=ReplyAction(content="You've specified an invalid site.")
        )
