from abc import ABCMeta

from hikari import CommandInteraction

from holobot.discord.workflows import IInteractionProcessor

# NOTE This interface is required, because otherwise the injectable contract
# would be the same as the CommandProcessor's, as both command and menu item
# interactions are represented by CommandInteraction.
class IMenuItemProcessor(IInteractionProcessor[CommandInteraction], metaclass=ABCMeta):
    """Interface for a context menu item related interaction processor."""
