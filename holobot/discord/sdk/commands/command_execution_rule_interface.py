from .command_interface import CommandInterface
from .models import ServerChatInteractionContext

class CommandExecutionRuleInterface:
    """Interface for a command execution rule.

    A rule is responsible for determining if a command's execution should be interrupted.
    """

    async def should_halt(self, command: CommandInterface, context: ServerChatInteractionContext) -> bool:
        """Determines if a given command should not be executed in the given context.

        Parameters
        ----------
        command : ``CommandInterface``
            The command to be validated.

        context : ``ServerChatInteractionContext``
            The current interaction context.
        
        Returns
        -------
        bool
            True, if the command should not be executed in the given context.
        """

        raise NotImplementedError
