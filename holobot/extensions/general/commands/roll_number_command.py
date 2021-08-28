from holobot.discord.sdk.actions import ReplyAction
from holobot.discord.sdk.commands import CommandBase, CommandInterface
from holobot.discord.sdk.commands.enums import OptionType
from holobot.discord.sdk.commands.models import CommandResponse, Option, ServerChatInteractionContext
from holobot.sdk.ioc.decorators import injectable
from random import randint

@injectable(CommandInterface)
class RollNumberCommand(CommandBase):
    def __init__(self) -> None:
        super().__init__("roll")
        self.description = "Generates a random integer between the specified bounds."
        self.options = [
            Option("max", "The upper bound.", OptionType.INTEGER, True),
            Option("min", "The lower bound. By default, it's 1.", OptionType.INTEGER, False)
        ]

    async def execute(self, context: ServerChatInteractionContext, max: int, min: int = 1) -> CommandResponse:
        if max < min:
            (min, max) = (max, min)
        return CommandResponse(
            action=ReplyAction(content=f"You rolled {randint(min, max)}.")
        )
