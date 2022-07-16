from abc import ABCMeta

from hikari import CommandInteraction

from holobot.discord.workflows import IInteractionProcessor

class IMenuItemProcessor(IInteractionProcessor[CommandInteraction], metaclass=ABCMeta):
    """Interface for a context menu item related interaction processor."""
