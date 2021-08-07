from .command_interface import CommandInterface
from discord_slash import SlashContext

class CommandExecutionRuleInterface:
    """Interface for a command execution rule.

    A rule is responsible for determining if a command's execution should be interrupted.
    """

    async def should_halt(self, command: CommandInterface, context: SlashContext) -> bool:
        """Determines if a given command should not be executed in the given context.

        Parameters
        ----------
        command : ``CommandInterface``
            The command to be validated.

        context : ``SlashContext``
            The current slash command context.
        
        Returns
        -------
        bool
            True, if the command should not be executed in the given context.
        """

        raise NotImplementedError
