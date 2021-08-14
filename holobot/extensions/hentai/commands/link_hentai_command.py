from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface, CommandResponse
from holobot.discord.sdk.utils import reply
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
            create_option("site", "The name of the site.", SlashCommandOptionType.STRING, True, choices=[
                create_choice(NHENTAI_SITE_ID, "nhentai"),
                create_choice(EHENTAI_SITE_ID, "e-hentai")
            ]),
            create_option("id", "The identifier of the title.", SlashCommandOptionType.STRING, True)
        ]
    
    async def execute(self, context: SlashContext, site: str, id: str) -> CommandResponse:
        if not site or not id:
            await reply(context, "You must specify both the site and the identifier.")
            return CommandResponse()
        id = id.strip()
        if site == NHENTAI_SITE_ID:
            if (value := try_parse_int(id)) is None:
                await reply(context, "Invalid identifier. A valid identifier, for example, is _206981_.")
                return CommandResponse()
            await reply(context, f"https://nhentai.net/g/{value}")
        elif site == EHENTAI_SITE_ID:
            if not ehentai_regex.match(id):
                await reply(context, "Invalid identifier. A valid identifier, for example, is _1383239/0e7abac58a_ (case-sensitive).")
                return CommandResponse()
            await reply(context, f"https://e-hentai.org/g/{id}")
        else: await reply(context, "You've specified an invalid site.")
        return CommandResponse()
