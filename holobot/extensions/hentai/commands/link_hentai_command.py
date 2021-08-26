from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.models import Choice, CommandResponse, Option, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from holobot.sdk.utils import try_parse_int

import re

NHENTAI_SITE_ID = "nhentai"
EHENTAI_SITE_ID = "ehentai"

ehentai_regex = re.compile(r"^(?:\d+)\/(?:[a-z0-9]{10})$")

@injectable(CommandInterface)
class LinkHentaiCommand(CommandBase):
    def __init__(self) -> None:
        super().__init__("link")
        self.group_name = "hentai"
        self.description = "Gives you a link to a title on a specific site."
        self.options = [
            Option("site", "The name of the site.", choices=[
                Choice("nhentai", NHENTAI_SITE_ID),
                Choice("e-hentai", EHENTAI_SITE_ID)
            ]),
            Option("id", "The identifier of the title.")
        ]
    
    async def execute(self, context: ServerChatInteractionContext, site: str, id: str) -> CommandResponse:
        if not site or not id:
            return CommandResponse(
                action=ReplyAction(content="You must specify both the site and the identifier.")
            )
        id = id.strip()
        if site == NHENTAI_SITE_ID:
            if (value := try_parse_int(id)) is None:
                return CommandResponse(
                    action=ReplyAction(content="Invalid identifier. A valid identifier, for example, is _206981_.")
                )
            return CommandResponse(
                action=ReplyAction(content=f"https://nhentai.net/g/{value}")
            )
        elif site == EHENTAI_SITE_ID:
            if not ehentai_regex.match(id):
                return CommandResponse(
                    action=ReplyAction(content="Invalid identifier. A valid identifier, for example, is _1383239/0e7abac58a_ (case-sensitive).")
                )
            return CommandResponse(
                action=ReplyAction(content=f"https://e-hentai.org/g/{id}")
            )

        return CommandResponse(
            action=ReplyAction(content="You've specified an invalid site.")
        )
