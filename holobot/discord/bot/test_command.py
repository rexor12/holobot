from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_choice, create_option
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.utils import reply
from holobot.sdk.ioc import ServiceCollectionInterface
from holobot.sdk.ioc.decorators import injectable

@injectable(CommandInterface)
class TestCommand(CommandBase):
    def __init__(self, services: ServiceCollectionInterface) -> None:
        super().__init__("two")
        self.group_name = "one"
        self.subgroup_name = "or"
        self.description = "A test command."
        self.options = [
            create_option("num", "A number.", SlashCommandOptionType.STRING, True, [
                create_choice("1", "one"),
                create_choice("2", "two"),
                create_choice("3", "three")
            ])
        ]

    async def execute(self, context: SlashContext, num: str) -> None:
        if num == "3":
            await reply(context, "There's no 3 <:GabAngry:822229895630815312>")
        else: await reply(context, f"Oke boi, it's {num}")
